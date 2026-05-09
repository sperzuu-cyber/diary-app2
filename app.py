from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"

DATABASE = "database.db"


# -----------------------------
# DATABASE HELPERS
# -----------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def column_exists(db, table_name, column_name):
    columns = db.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(column["name"] == column_name for column in columns)


def init_db():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            no_contact_start_date TEXT,
            no_contact_end_date TEXT
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            entry_type TEXT NOT NULL,
            content TEXT NOT NULL,
            mood TEXT,
            is_public INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    if not column_exists(db, "entries", "is_public"):
        db.execute("ALTER TABLE entries ADD COLUMN is_public INTEGER DEFAULT 0")

    db.execute("""
        CREATE TABLE IF NOT EXISTS urges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            trigger TEXT,
            message_they_wanted_to_send TEXT,
            hoped_reply TEXT,
            ignored_feeling TEXT,
            did_contact_ex INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    db.commit()


@app.before_request
def before_request():
    init_db()


# -----------------------------
# AUTH HELPERS
# -----------------------------
def current_user():
    if "user_id" not in session:
        return None

    db = get_db()
    return db.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()


def login_required():
    if "user_id" not in session:
        flash("Please log in first.", "warning")
        return False
    return True


def calculate_streak(user):
    if not user or not user["no_contact_start_date"]:
        return 0

    start = datetime.strptime(user["no_contact_start_date"], "%Y-%m-%d").date()
    today = date.today()
    return max((today - start).days, 0)


# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def home():
    user = current_user()
    streak = calculate_streak(user) if user else 0
    return render_template("home.html", user=user, streak=streak)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)
        today = date.today().isoformat()

        db = get_db()

        try:
            db.execute(
                """
                INSERT INTO users (username, password_hash, no_contact_start_date)
                VALUES (?, ?, ?)
                """,
                (username, password_hash, today)
            )
            db.commit()
            flash("Account created. Your no-contact streak starts today.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("That username already exists.", "danger")
            return redirect(url_for("register"))

    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            flash("You are back. Choose yourself again today.", "success")
            return redirect(url_for("home"))

        flash("Invalid username or password.", "danger")
        return redirect(url_for("login"))

    return render_template("auth.html", mode="login")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out safely.", "info")
    return redirect(url_for("home"))


@app.route("/write-instead", methods=["GET", "POST"])
def write_instead():
    if not login_required():
        return redirect(url_for("login"))

    if request.method == "POST":
        trigger = request.form.get("trigger", "")
        custom_trigger = request.form.get("custom_trigger", "").strip()
        message = request.form.get("message_they_wanted_to_send", "").strip()
        hoped_reply = request.form.get("hoped_reply", "").strip()
        ignored_feeling = request.form.get("ignored_feeling", "").strip()
        is_public = 1 if request.form.get("is_public") == "on" else 0

        if custom_trigger:
            trigger = custom_trigger

        if not message:
            flash("Write the message here instead of sending it.", "warning")
            return redirect(url_for("write_instead"))

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = get_db()

        db.execute(
            """
            INSERT INTO urges
            (user_id, trigger, message_they_wanted_to_send, hoped_reply, ignored_feeling, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session["user_id"], trigger, message, hoped_reply, ignored_feeling, now)
        )

        db.execute(
            """
            INSERT INTO entries
            (user_id, entry_type, content, mood, is_public, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session["user_id"], "unsent_message", message, trigger, is_public, now)
        )

        db.commit()

        flash("Saved. You did not send it. That counts.", "success")
        return redirect(url_for("streak"))

    return render_template("write_instead.html", user=current_user())


@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    if not login_required():
        return redirect(url_for("login"))

    if request.method == "POST":
        mood = request.form.get("mood", "")
        content = request.form.get("content", "").strip()
        is_public = 1 if request.form.get("is_public") == "on" else 0

        if not content:
            flash("Write at least one honest sentence.", "warning")
            return redirect(url_for("checkin"))

        db = get_db()
        db.execute(
            """
            INSERT INTO entries
            (user_id, entry_type, content, mood, is_public, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                "daily_checkin",
                content,
                mood,
                is_public,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        db.commit()

        flash("Check-in saved. You are processing instead of chasing.", "success")
        return redirect(url_for("journal"))

    return render_template("checkin.html", user=current_user())


@app.route("/journal")
def journal():
    if not login_required():
        return redirect(url_for("login"))

    db = get_db()
    entries = db.execute(
        """
        SELECT * FROM entries
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    urges = db.execute(
        """
        SELECT * FROM urges
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    return render_template("journal.html", entries=entries, urges=urges, user=current_user())


@app.route("/public-vault")
def public_vault():
    db = get_db()

    entries = db.execute(
        """
        SELECT entries.*, users.username
        FROM entries
        JOIN users ON entries.user_id = users.id
        WHERE entries.is_public = 1
        ORDER BY entries.created_at DESC
        """
    ).fetchall()

    return render_template("public_vault.html", entries=entries, user=current_user())


@app.route("/streak")
def streak():
    if not login_required():
        return redirect(url_for("login"))

    user = current_user()
    streak_days = calculate_streak(user)

    return render_template("streak.html", user=user, streak=streak_days)


@app.route("/relapse", methods=["POST"])
def relapse():
    if not login_required():
        return redirect(url_for("login"))

    db = get_db()
    today = date.today().isoformat()

    db.execute(
        """
        UPDATE users
        SET no_contact_start_date = ?, no_contact_end_date = ?
        WHERE id = ?
        """,
        (today, today, session["user_id"])
    )

    db.execute(
        """
        INSERT INTO entries
        (user_id, entry_type, content, mood, is_public, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            "relapse_reset",
            "Healing is not linear. I am starting again without shame.",
            "reset",
            0,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    db.commit()

    flash("Healing isn’t linear. Start again with self-respect.", "info")
    return redirect(url_for("streak"))


@app.route("/timer")
def timer():
    if not login_required():
        return redirect(url_for("login"))

    return render_template("timer.html", user=current_user())


if __name__ == "__main__":
    app.run(debug=True)