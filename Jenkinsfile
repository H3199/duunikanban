pipeline {
    agent any

    environment {
        COMPOSE_FILE = "docker-compose.yml"
        PYTEST_PATH = "tests"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Load env file') {
            steps {
                sh '''
                bash -c "set -o allexport; source /var/jenkins_home/envs/duunihaku.env; set +o allexport"
                '''
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh """
                        echo "Running tests inside Docker image"
                        docker build -t duunihaku-test .
                        docker run --rm duunihaku-test pytest -v tests
                    """
                }
            }
        }

        stage('Deploy with Docker Compose') {
            when {
                expression { currentBuild.currentResult == 'SUCCESS' }
            }
            steps {
                script {
                    sh """
                        echo "--- Deploying Docker Stack ---"
                        docker compose down || true
                        docker compose pull || true
                        docker compose up -d --build
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Duunihaku deployed successfully.'
        }
        failure {
            echo 'Build or deployment failed. Check the logs for details.'
        }
    }
}
