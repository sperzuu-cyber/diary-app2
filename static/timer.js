let timeLeft = 600;
let timerInterval = null;
let currentResource = 0;
let resourceRotation = null;

const prompts = [
    "What pain are you trying to make them fix?",
    "If they ignore you, will you feel better or worse?",
    "Are you contacting them for love, or relief?",
    "What would the healed version of you do right now?",
    "What are you hoping they say back?",
    "What would protecting your dignity look like tonight?",
    "Would sending this message protect your peace or restart the wound?",
    "Are you missing them, or missing the version of them you hoped they would become?",
    "What would you do right now if you truly believed you were enough?"
];

const resources = [
    {
        title: "Mel Robbins",
        message: "Stop chasing closure. Choose yourself again. Let them.",
        link: "https://www.youtube.com/results?search_query=mel+robbins+breakup",
        video: "c1orPqt6Wr0"
    },
    {
        title: "Jay Shetty",
        message: "Relationship healing, self-worth, emotional maturity, letting go and moving forward.",
        link: "https://www.youtube.com/results?search_query=jay+shetty+breakup",
        video: "nxxAZ6CUU-M"
    },
    {
        title: "Liz The Wizard",
        message: "Self-concept, detachment, emotional control, rebuilding confidence after heartbreak.",
        link: "https://www.youtube.com/results?search_query=liz+the+wizard+self+concept",
        video: "x0DTdXEd3mQ"
    },
    {
        title: "Healing playlist",
        message: "Music for late nights, emotional crashes, and moments where you almost text them.",
        link: "https://open.spotify.com/search/breakup%20healing%20playlist"
    },
    {
        title: "Calm your nervous system",
        message: "Your brain is looking for relief, not necessarily them. Breathe before you decide.",
        link: "https://www.youtube.com/results?search_query=guided+breathing+exercise+anxiety",
        video: "xYBZUcr9XrQ"
    },
    {
        title: "Attachment healing",
        message: "Understand anxious attachment, emotional dependency, and obsession loops.",
        link: "https://www.youtube.com/results?search_query=attachment+style+healing+breakup",
        video: "CPZnScHa1d0"
    },
    {
        title: "Gym suggestion",
        message: "Redirect the emotional energy into movement. Train instead of spiralling.",
        link: "https://www.youtube.com/results?search_query=beginner+gym+workout",
        video: "cbKkB3POqaY"
    },
    {
        title: "Walk or hike",
        message: "Leave the room. Change your environment. Let the urge pass physically.",
        link: "https://www.google.com/maps/search/parks+near+me"
    },
    {
        title: "Motivational reset",
        message: "Remember who you were before this relationship consumed you.",
        link: "https://www.youtube.com/results?search_query=self+respect+motivation",
        video: "kYg79NYLWnc"
    }
];

function updateDisplay() {
    const timer = document.getElementById("timer");
    if (!timer) return;

    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;

    timer.innerText = `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

function showResource(index) {
    const resource = resources[index];

    document.getElementById("resource-title").innerText = resource.title;
    document.getElementById("resource-message").innerText = resource.message;
    document.getElementById("resource-link").href = resource.link;

    const video = document.getElementById("resource-video");
    const videoBox = document.getElementById("video-preview-box");

    if (resource.video) {
        video.src = `https://www.youtube.com/embed/${resource.video}`;
        videoBox.style.display = "block";
    } else {
        video.src = "";
        videoBox.style.display = "none";
    }
}

function nextResource() {
    currentResource = (currentResource + 1) % resources.length;
    showResource(currentResource);
}

function startResourceRotation() {
    if (resourceRotation !== null) return;

    resourceRotation = setInterval(() => {
        nextResource();
    }, 4000);
}

function stopResourceRotation() {
    clearInterval(resourceRotation);
    resourceRotation = null;
}

document.addEventListener("DOMContentLoaded", () => {
    updateDisplay();
    showResource(currentResource);
    startResourceRotation();

    const videoBox = document.getElementById("video-preview-box");

    if (videoBox) {
        videoBox.addEventListener("mouseenter", stopResourceRotation);
        videoBox.addEventListener("touchstart", stopResourceRotation);
        videoBox.addEventListener("mouseleave", startResourceRotation);
    }
});

function startTimer() {
    if (timerInterval) return;

    timerInterval = setInterval(() => {
        timeLeft--;
        updateDisplay();

        if (timeLeft % 90 === 0) {
            const randomPrompt = prompts[Math.floor(Math.random() * prompts.length)];
            document.getElementById("prompt").innerText = randomPrompt;
            nextResource();
        }

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            timerInterval = null;

            document.getElementById("prompt").innerText =
                "You waited. That is emotional control. Now write it here instead of sending it.";
        }
    }, 1000);
}

document.addEventListener("DOMContentLoaded", () => {
    updateDisplay();
    showResource(currentResource);
    startResourceRotation();

    const videoBox = document.getElementById("video-preview-box");

    if (videoBox) {
        videoBox.addEventListener("click", () => {
            stopResourceRotation();
        });
    }
});