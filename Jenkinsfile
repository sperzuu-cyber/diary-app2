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
                sudo mkdir -p /home/ubuntu/diary-app2
                sudo mkdir -p /home/ubuntu/break-loop-data

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

                sudo /usr/bin/chown -R ubuntu:ubuntu /home/ubuntu/break-loop-data
                sudo /usr/bin/chmod 775 /home/ubuntu/break-loop-data

                if [ -f /home/ubuntu/break-loop-data/database.db ]; then
                  sudo /usr/bin/chmod 664 /home/ubuntu/break-loop-data/database.db
                fi
                '''
            }
        }

        stage('Build Docker image') {
            steps {
                sh '''
                cd /home/ubuntu/diary-app2
                sudo DOCKER_BUILDKIT=0 docker build -t my-flask-app .
                '''
            }
        }

        stage('Restart Docker container') {
            steps {
                sh '''
                sudo docker rm -f my-flask-container || true

                sudo docker run -d \
                  --name my-flask-container \
                  --restart unless-stopped \
                  -p 5000:5000 \
                  -v /home/ubuntu/break-loop-data:/home/ubuntu/break-loop-data \
                  my-flask-app
                '''
            }
        }

        stage('Check app') {
            steps {
                sh '''
                sleep 5
                sudo docker ps
                curl -f http://localhost:5000/login || (sudo docker logs my-flask-container --tail 80 && exit 1)
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment successful. Docker container is live.'
        }

        failure {
            echo 'Deployment failed. Check Jenkins console output and Docker logs.'
        }
    }
}