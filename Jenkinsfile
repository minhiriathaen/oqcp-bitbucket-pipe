pipeline {
    agent any

    environment {
        MOCKOON_IMAGE_NAME = "oqcp/mockoon-pipe-${env.EXECUTOR_NUMBER}:${BUILD_NUMBER}"
        OQCP_TEST_NETWORK_NAME = "oqcp-pipe-test-network-${env.EXECUTOR_NUMBER}-${BUILD_NUMBER}"
        MOCKOON_OQC_CONTAINER_NAME = "mockoon-openqualitychecker-pipe-${env.EXECUTOR_NUMBER}-${BUILD_NUMBER}"
    }

    stages {
        stage("Start API mocks") {
            agent any

            steps {
                dir('test/Mockoon') {
                    sh "docker build -t ${env.MOCKOON_IMAGE_NAME} ."
                    sh "docker network create --driver bridge ${env.OQCP_TEST_NETWORK_NAME} || true"
                    sh """
                        docker run -d --name ${env.MOCKOON_OQC_CONTAINER_NAME} --rm \
                            --network=${env.OQCP_TEST_NETWORK_NAME} \
                            --hostname=mockoon-openqualitychecker \
                            ${env.MOCKOON_IMAGE_NAME} \
                            -d data -n "OpenQualityChecker" -p 3000
                        """
                }
            }
        }

        stage('Test') {
            agent {
                docker {
                    image 'python:3.7'
                    args "-u root --network=${env.OQCP_TEST_NETWORK_NAME}"
                }
            }

            steps {
                sh 'pip install -r requirements.txt'
                sh 'pytest -v pipe/test_native.py'
            }
        }
    }

    post {
        always {
            sh "docker rm -vf ${env.MOCKOON_OQC_CONTAINER_NAME} || true"
            sh "docker network rm ${env.OQCP_TEST_NETWORK_NAME} || true"
            sh "docker rmi -f ${MOCKOON_IMAGE_NAME} || true"
        }
    }
}
