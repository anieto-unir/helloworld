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
                                rm -rf venv-unit
                                python3 -m venv venv-unit
                                . venv-unit/bin/activate
                                pip install --upgrade pip
                                pip install -r requirements.txt
                                pip install -e .
                                
                                # Ejecutar tests CON cobertura (una sola vez)
                                pytest --cov=app --cov-branch --cov-report=xml --cov-report=html \
                                       --junitxml=result-unit.xml test/unit
                            '''
                        }
                        junit 'result-unit.xml'
                        
                        // Guardar archivos de cobertura para el stage Coverage
                        stash includes: 'coverage.xml,htmlcov/**,.coverage', name: 'coverage-data'
                    }
                }

                stage('Rest') {
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            sh '''
                                export PYTHONPATH=$PWD
                                rm -rf venv-rest
                                python3 -m venv venv-rest
                                . venv-rest/bin/activate
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
                                rm -rf venv-static
                                python3 -m venv venv-static
                                . venv-static/bin/activate
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
                        archiveArtifacts artifacts: 'flake8.log', allowEmptyArchive: true
                    }
                }

                stage('Security') {
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            sh '''
                                rm -rf venv-security
                                python3 -m venv venv-security
                                . venv-security/bin/activate
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
                        recordIssues tools: [pmdParser(name: 'Bandit', pattern: 'bandit-report.json')]
                        archiveArtifacts artifacts: 'bandit-report.*', allowEmptyArchive: true
                    }
                }
            }
        }

        stage('Performance') {
            steps {
                sh '''
                    export PYTHONPATH=$PWD
                    rm -rf venv-perf
                    python3 -m venv venv-perf
                    . venv-perf/bin/activate
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
                archiveArtifacts artifacts: 'jmeter-results.jtl,jmeter-report/**/*', allowEmptyArchive: true
                perfReport sourceDataFiles: 'jmeter-results.jtl'
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'jmeter-report',
                    reportFiles: 'index.html',
                    reportName: 'JMeter Performance Report'
                ])
            }
        }

        stage('Coverage') {
            steps {
                // Recuperar archivos de cobertura generados en stage Unit
                unstash 'coverage-data'
                
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh '''
                        # Extraer cobertura del archivo ya generado
                        COVERAGE_LINE=$(python3 -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); root = tree.getroot(); print(float(root.attrib['line-rate']) * 100)")
                        COVERAGE_BRANCH=$(python3 -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); root = tree.getroot(); print(float(root.attrib['branch-rate']) * 100)")

                        echo "Line coverage: ${COVERAGE_LINE}%"
                        echo "Branch coverage: ${COVERAGE_BRANCH}%"

                        # Aplicar baremo según enunciado
                        # Líneas: <85% rojo, 85-95% unstable, >95% verde
                        # Ramas: <80% rojo, 80-90% unstable, >90% verde
                        
                        LINE_FAIL=$(python3 -c "print(1 if ${COVERAGE_LINE} < 85.0 else 0)")
                        BRANCH_FAIL=$(python3 -c "print(1 if ${COVERAGE_BRANCH} < 80.0 else 0)")
                        LINE_UNSTABLE=$(python3 -c "print(1 if 85.0 <= ${COVERAGE_LINE} < 95.0 else 0)")
                        BRANCH_UNSTABLE=$(python3 -c "print(1 if 80.0 <= ${COVERAGE_BRANCH} < 90.0 else 0)")

                        # Evaluar resultado según baremo
                        if [ "$LINE_FAIL" -eq 1 ] || [ "$BRANCH_FAIL" -eq 1 ]; then
                            echo "FAILURE: Coverage below minimum thresholds (RED)"
                            if [ "$LINE_FAIL" -eq 1 ]; then
                                echo "  - Line coverage: ${COVERAGE_LINE}% < 85% (minimum)"
                            fi
                            if [ "$BRANCH_FAIL" -eq 1 ]; then
                                echo "  - Branch coverage: ${COVERAGE_BRANCH}% < 80% (minimum)"
                            fi
                            exit 1
                        elif [ "$LINE_UNSTABLE" -eq 1 ] || [ "$BRANCH_UNSTABLE" -eq 1 ]; then
                            echo "UNSTABLE: Coverage in acceptable range but below optimal (YELLOW)"
                            echo "  - Line coverage: ${COVERAGE_LINE}% (target: >95%)"
                            echo "  - Branch coverage: ${COVERAGE_BRANCH}% (target: >90%)"
                            exit 1
                        else
                            echo "SUCCESS: Coverage meets all thresholds (GREEN)"
                            echo "  - Line coverage: ${COVERAGE_LINE}% >= 95%"
                            echo "  - Branch coverage: ${COVERAGE_BRANCH}% >= 90%"
                        fi
                    '''
                }
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
                archiveArtifacts artifacts: 'coverage.xml', allowEmptyArchive: true
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