pipeline {
    agent any

    triggers {
        githubPush()
    }

    stages {
        stage('Checkout latest code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/sperzuu-cyber/diary-app2.git'
            }
        }

        stage('Validate Python') {
            steps {
                sh '''
                python3 -m py_compile app.py
                '''
            }
        }

        stage('Deploy code to app folder') {
            steps {
                sh '''
                sudo /usr/bin/rsync -av --delete \
                --exclude 'venv' \
                --exclude 'database.db' \
                --exclude 'database.db-journal' \
                --exclude 'database.db-wal' \
                --exclude 'database.db-shm' \
                --exclude '.git' \
                --exclude '__pycache__' \
                --exclude 'static/uploads' \
                ./ /home/ubuntu/diary-app2/

                sudo /usr/bin/chown -R ubuntu:ubuntu /home/ubuntu/diary-app2
                sudo /usr/bin/chmod 775 /home/ubuntu/diary-app2
                sudo /usr/bin/chmod 664 /home/ubuntu/diary-app2/database.db
                '''
            }
        }

        stage('Restart app') {
            steps {
                sh '''
                sudo /usr/bin/systemctl restart diary-app.service
                '''
            }
        }

        stage('Check app') {
            steps {
                sh '''
                sleep 3
                curl -f http://localhost:5000/login
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment successful. Website is live.'
        }

        failure {
            echo 'Deployment failed. Check Jenkins console output and diary-app.service logs.'
        }
    }
}