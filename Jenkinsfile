pipeline {
    agent any

    stages {
        stage('Get Code') {
            steps {
                // Obtener código del repo
                git branch: 'feature/practice-1.1', url:'https://github.com/gCuadros/helloworld-devops.git'
                sh 'ls -la'
                echo WORKSPACE
            }
        }


        stage('Build') {
            steps {
                echo 'Eyyy, esto es Python. No hay que compilar nada!!!'
                echo 'Installing dependencies...'
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install --upgrade pip'
                sh '. venv/bin/activate && pip install -r requirements.txt'
                sh '. venv/bin/activate && pip install -e .'
            }
        }

        stage('Tests') {
            parallel {
                stage('Unit') {
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            sh '''
                                export PYTHONPATH=.
                                . venv/bin/activate
                                pytest --junitxml=result-unit.xml test/unit
                            '''
                        }
                    }
                }

                stage('Rest') {
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            sh '''
                                . venv/bin/activate
                                export FLASK_APP=app/api.py

                                # Iniciar Flask en background
                                nohup flask run --port 5001 > flask.log 2>&1 &
                                echo $! > flask.pid

                                # Descargar Wiremock si no existe
                                if [ ! -f "wiremock-standalone.jar" ]; then
                                    echo "Downloading Wiremock..."
                                    curl -o wiremock-standalone.jar https://repo1.maven.org/maven2/com/github/tomakehurst/wiremock-standalone/2.27.2/wiremock-standalone-2.27.2.jar
                                fi
                                nohup java -jar wiremock-standalone.jar --port 9090 --root-dir test/wiremock > wiremock.log 2>&1 &
                                echo $! > wiremock.pid

                                # Esperar a que los servicios arranquen
                                echo "Waiting for Flask to start..."
                                sleep 8
                                echo "Waiting for Wiremock to start..."
                                sleep 5

                                # Ejecutar tests REST
                                pytest --junitxml=result-rest.xml test/rest
                            '''
                        }
                    }
                }
            }
        }

        stage('Results') {
            steps {
                junit 'result*.xml'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up services...'
            sh '''
                if [ -f flask.pid ]; then
                    kill $(cat flask.pid) 2>/dev/null || true
                    rm flask.pid
                fi
                if [ -f wiremock.pid ]; then
                    kill $(cat wiremock.pid) 2>/dev/null || true
                    rm wiremock.pid
                fi
            '''
        }
        success {
            echo '========================================='
            echo 'Pipeline executed successfully!'
            echo 'All tests passed!'
            echo '========================================='
        }
        failure {
            echo '========================================='
            echo 'Pipeline failed!'
            echo 'Check logs above for details'
            echo '========================================='
        }
    }
}
