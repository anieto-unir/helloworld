pipeline {
    agent any

    options {
        skipDefaultCheckout true
    }

    stages {
        stage('Get Code') {
            steps {
                // Obtener código del repositorio
                git branch: 'feature/practice-1.2', url: 'https://github.com/gCuadros/helloworld-devops.git'

                echo "Code checked out successfully"
            }
        }

        stage('Tests') {
            parallel {
                stage('Unit') {
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            sh '''
                                export PYTHONPATH=$PWD
                                python3 -m venv venv
                                . venv/bin/activate
                                pip install --upgrade pip
                                pip install -r requirements.txt
                                pip install -e .
                                pytest --junitxml=result-unit.xml test/unit
                            '''
                        }
                        junit 'result-unit.xml'
                    }
                }

                stage('Rest') {
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            sh '''
                                export PYTHONPATH=$PWD
                                python3 -m venv venv
                                . venv/bin/activate
                                pip install --upgrade pip
                                pip install -r requirements.txt
                                pip install -e .

                                export FLASK_APP=app/api.py

                                # Iniciar Flask en background
                                nohup flask run --port 5001 > flask.log 2>&1 &
                                echo $! > flask.pid
                                sleep 4

                                # Descargar Wiremock si no existe
                                if [ ! -f "wiremock-standalone.jar" ]; then
                                    echo "Downloading Wiremock..."
                                    curl -o wiremock-standalone.jar https://repo1.maven.org/maven2/com/github/tomakehurst/wiremock-standalone/2.27.2/wiremock-standalone-2.27.2.jar
                                fi
                                nohup java -jar wiremock-standalone.jar --port 9090 --root-dir test/wiremock > wiremock.log 2>&1 &
                                echo $! > wiremock.pid

                                echo "Waiting for services to start..."
                                sleep 10

                                # Ejecutar tests REST
                                pytest --junitxml=result-rest.xml test/rest

                                # Limpiar servicios
                                kill $(cat flask.pid) 2>/dev/null || true
                                kill $(cat wiremock.pid) 2>/dev/null || true
                            '''
                        }
                        junit 'result-rest.xml'
                    }
                }

                stage('Static') {
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            sh '''
                                python3 -m venv venv
                                . venv/bin/activate
                                pip install --upgrade pip
                                pip install flake8 flake8-html

                                # Ejecutar Flake8 en app/
                                flake8 --exit-zero --format=pylint --output-file=flake8.log app/

                                # Contar errores
                                ERRORS=$(grep -c "^\\[" flake8.log || echo "0")
                                echo "Flake8 found $ERRORS issues"

                                # Aplicar baremo
                                if [ "$ERRORS" -ge 10 ]; then
                                    echo "UNHEALTHY: 10 or more issues found"
                                    exit 1
                                elif [ "$ERRORS" -ge 8 ]; then
                                    echo "UNSTABLE: 8-9 issues found"
                                    exit 1
                                else
                                    echo "HEALTHY: Less than 8 issues found"
                                fi
                            '''
                        }
                        recordIssues tools: [flake8(name: 'Flake8', pattern: 'flake8.log')]
                    }
                }

                stage('Security') {
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            sh '''
                                python3 -m venv venv
                                . venv/bin/activate
                                pip install --upgrade pip
                                pip install bandit

                                # Ejecutar Bandit
                                bandit -r app/ -f json -o bandit-report.json --exit-zero || true
                                bandit -r app/ -f txt -o bandit-report.txt --exit-zero || true

                                # Contar issues
                                ISSUES=$(python3 -c "import json; data=json.load(open('bandit-report.json')); print(len(data.get('results', [])))" 2>/dev/null || echo "0")
                                echo "Bandit found $ISSUES security issues"

                                # Aplicar baremo
                                if [ "$ISSUES" -ge 4 ]; then
                                    echo "UNHEALTHY: 4 or more security issues"
                                    exit 1
                                elif [ "$ISSUES" -ge 2 ]; then
                                    echo "UNSTABLE: 2-3 security issues"
                                    exit 1
                                else
                                    echo "HEALTHY: Less than 2 security issues"
                                fi
                            '''
                        }
                        archiveArtifacts artifacts: 'bandit-report.*', allowEmptyArchive: true
                    }
                }
            }
        }

        stage('Performance') {
            steps {
                sh '''
                    export PYTHONPATH=$PWD
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install -e .

                    export FLASK_APP=app/api.py

                    # Iniciar Flask
                    nohup flask run --port 5001 > flask.log 2>&1 &
                    echo $! > flask.pid
                    sleep 5

                    # Verificar que Flask responde
                    curl -f http://localhost:5001/ || echo "Flask not responding"

                    # Ejecutar JMeter
                    jmeter -n -t test/jmeter/flask.jmx -l jmeter-results.jtl -e -o jmeter-report || echo "JMeter completed with warnings"

                    # Limpiar
                    kill $(cat flask.pid) 2>/dev/null || true
                '''
                perfReport sourceDataFiles: 'jmeter-results.jtl', errorUnstableThreshold: 0, errorFailedThreshold: 5
            }
        }

        stage('Coverage') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh '''
                        export PYTHONPATH=$PWD
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install -e .

                        # Ejecutar tests con cobertura
                        pytest --cov=app --cov-report=xml --cov-report=html --cov-report=term test/unit

                        # Extraer cobertura
                        COVERAGE_LINE=$(python3 -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); root = tree.getroot(); print(float(root.attrib['line-rate']) * 100)")
                        COVERAGE_BRANCH=$(python3 -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); root = tree.getroot(); print(float(root.attrib['branch-rate']) * 100)")

                        echo "Line coverage: ${COVERAGE_LINE}%"
                        echo "Branch coverage: ${COVERAGE_BRANCH}%"

                        # Aplicar baremo
                        LINE_OK=$(python3 -c "print(1 if ${COVERAGE_LINE} >= 85.0 else 0)")
                        BRANCH_OK=$(python3 -c "print(1 if ${COVERAGE_BRANCH} >= 80.0 else 0)")

                        if [ "$LINE_OK" -eq 0 ] || [ "$BRANCH_OK" -eq 0 ]; then
                            echo "UNSTABLE: Coverage below minimum (Line: 85%, Branch: 80%)"
                            exit 1
                        fi
                    '''
                }
                publishHTML([
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
                cobertura coberturaReportFile: 'coverage.xml'
            }
        }
    }

    post {
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