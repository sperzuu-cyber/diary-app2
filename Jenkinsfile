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

        stage('Deploy code to app folder') {
            steps {
                sh '''
                sudo rsync -av --delete \
                --exclude 'venv' \
                --exclude 'database.db' \
                --exclude '.git' \
                --exclude '__pycache__' \
                --exclude 'static/uploads' \
                ./ /home/ubuntu/diary-app2/
                
                sudo chown -R ubuntu:ubuntu /home/ubuntu/diary-app2
                sudo chmod 775 /home/ubuntu/diary-app2
                sudo chmod 664 /home/ubuntu/diary-app2/database.db
                '''
            }
        }

        stage('Restart app') {
            steps {
                sh '''
                sudo /bin/systemctl restart diary-app.service
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