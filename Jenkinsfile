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

        stage('Run Tests') {
            steps {
                script {
                    sh """
                        echo "--- Running tests ---"
                        pip3 install -r requirements.txt >/dev/null 2>&1 || true
                        pytest -v ${PYTEST_PATH}
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
