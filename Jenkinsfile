pipeline {
    // Option 1: Use any agent except the master node
    // agent { label '!master' }

    // Option 2: Use a specific local agent
    // agent { label 'agent-local' }

    // Option 3: Use dynamic Docker agent 
    // agent { label 'docker-python' }

    // Option 4: Keep 'any' 
    agent any

    environment {
        PYTHON_VERSION = '3.9'
    }

    stages {
        stage('Setup') {
            steps {
                echo 'Setting up Python environment...'
                sh 'python3 --version'
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install --upgrade pip'
                sh '. venv/bin/activate && pip install -r requirements.txt'
                sh '. venv/bin/activate && pip install -e .'
            }
        }

        stage('Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh 'mkdir -p reports'
                sh '. venv/bin/activate && pytest -v -m unit --junitxml=reports/unit-tests.xml'
            }
        }

        stage('Start Services') {
            steps {
                echo 'Starting Flask application...'
                sh '''
                    . venv/bin/activate
                    nohup python3 -m flask --app app.api run --port 5000 > flask.log 2>&1 &
                    echo $! > flask.pid
                    sleep 5
                    echo "Flask started with PID: $(cat flask.pid)"
                '''

                echo 'Starting Wiremock...'
                sh '''
                    if ! command -v wiremock &> /dev/null; then
                        echo "Wiremock not found. Installing via Homebrew..."
                        brew install wiremock-standalone
                    fi
                    nohup wiremock --port 9090 --root-dir test/wiremock > wiremock.log 2>&1 &
                    echo $! > wiremock.pid
                    sleep 3
                    echo "Wiremock started with PID: $(cat wiremock.pid)"
                '''

                echo 'Verifying services are running...'
                sh '''
                    curl -f http://localhost:5000/ || (echo "Flask failed to start" && exit 1)
                    curl -f http://localhost:9090/__admin || (echo "Wiremock failed to start" && exit 1)
                    echo "All services are running successfully"
                '''
            }
        }

        stage('API Tests') {
            steps {
                echo 'Running API integration tests...'
                sh '. venv/bin/activate && pytest -v -m api --junitxml=reports/api-tests.xml'
            }
        }

        stage('Code Coverage') {
            steps {
                echo 'Generating code coverage report...'
                sh '. venv/bin/activate && pytest --cov=app --cov-report=xml --cov-report=html'
            }
        }
    }

    post {
        always {
            echo 'Cleaning up services...'
            sh '''
                if [ -f flask.pid ]; then
                    echo "Stopping Flask (PID: $(cat flask.pid))"
                    kill $(cat flask.pid) || true
                    rm flask.pid
                fi
                if [ -f wiremock.pid ]; then
                    echo "Stopping Wiremock (PID: $(cat wiremock.pid))"
                    kill $(cat wiremock.pid) || true
                    rm wiremock.pid
                fi
            '''

            echo 'Publishing test results...'
            junit 'reports/*.xml'

            echo 'Publishing coverage report...'
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'htmlcov',
                reportFiles: 'index.html',
                reportName: 'Coverage Report',
                reportTitles: 'Code Coverage'
            ])
        }
        success {
            echo '========================================='
            echo 'Pipeline executed successfully!'
            echo 'All tests passed and services cleaned up'
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
