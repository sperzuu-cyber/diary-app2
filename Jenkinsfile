pipeline {
    agent any

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
                --exclude 'diary.db' \
                --exclude 'static/uploads' \
                ./ /home/ubuntu/diary-app2/
                '''
            }
        }

        stage('Restart app') {
            steps {
                sh '''
                sudo /bin/systemctl restart diary-app
                '''
            }
        }

        stage('Check app') {
            steps {
                sh '''
                sleep 3
                curl -f http://localhost:5000
                '''
            }
        }
    }
}



