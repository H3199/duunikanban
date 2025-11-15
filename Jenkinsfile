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

        stage('Load .env config') {
            steps {
                script {
                    def envFile = readFile("/var/jenkins_home/envs/duunihaku.env").split("\n")
                    envFile.each { line ->
                        if (line && !line.startsWith("#") && line.contains("=")) {
                            def (key, value) = line.split("=", 2)
                            env[key.trim()] = value.trim()
                        }
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh """
                docker build -t duunihaku-test .

                docker run --rm \
                    -e THEIRSTACK_API_KEY='${env.THEIRSTACK_API_KEY}' \
                    -e HOME_LAT='${env.HOME_LAT}' \
                    -e HOME_LON='${env.HOME_LON}' \
                    -e MOCK='${env.MOCK}' \
                    duunihaku-test pytest -v
                """
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                sh """
                docker compose down || true

                THEIRSTACK_API_KEY='${env.THEIRSTACK_API_KEY}' \
                HOME_LAT='${env.HOME_LAT}' \
                HOME_LON='${env.HOME_LON}' \
                MOCK='${env.MOCK}' \
                docker compose up -d --build
                """
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
