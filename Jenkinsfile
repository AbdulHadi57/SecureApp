pipeline {
    agent any

    tools {
        // Maven installed in Jenkins global tools (Manage Jenkins → Global Tools)
        maven 'Maven'
    }

     parameters {
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run Python unit tests?')
        booleanParam(name: 'RUN_MAVEN', defaultValue: false, description: 'Run Maven build stage?')
        string(name: 'BUILD_ENV', defaultValue: 'dev', description: 'Build environment (dev/stage/prod)')
    }

    
    environment {
        PYTHON_VERSION = '3.9'
        VENV_DIR = 'venv'
        APP_NAME = 'FirstApp'
        FLASK_ENV = "${params.BUILD_ENV}"
    }
    
    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out code from repository...'
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo "Setting up Python virtual environment (Python ${env.PYTHON_VERSION})..."
                bat '''
                    python --version
                    python -m venv %VENV_DIR%
                    call %VENV_DIR%\\Scripts\\activate.bat
                    python -m pip install --upgrade pip
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    if exist requirements.txt (
                        pip install -r requirements.txt
                    ) else (
                        echo "No requirements.txt found — skipping pip install"
                    )
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running unit tests...'
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    bat '''
                        call %VENV_DIR%\\Scripts\\activate.bat
                        pytest --verbose --junit-xml=test-results.xml
                    '''
                }
                echo '"Tests completed (even if no tests were collected)"'
            }
        }


        stage('Maven Build') {
            when {
                expression { return params.RUN_MAVEN == true }
            }
            steps {
                echo "Maven Build Stage Running..."
                script {
                    if (fileExists('pom.xml')) {
                        bat "mvn -B clean package"
                    } else {
                        echo "No pom.xml found — skipping Maven build"
                    }
                }
            }
        }
        
        stage('Database Migration Check') {
            steps {
                echo 'Checking database schema...'
                bat '''
                    call %VENV_DIR%\\Scripts\\activate.bat
                    python create_db.py
                '''
            }
        }
        
        stage('Build Artifact') {
            steps {
                echo "Creating deployment artifact for environment: ${params.BUILD_ENV}"
                bat '''
                    if exist dist rmdir /s /q dist
                    mkdir dist
                    if exist static xcopy /E /I /Y static dist\\static
                    if exist templates xcopy /E /I /Y templates dist\\templates
                    if exist app.py copy app.py dist\\
                    if exist create_db.py copy create_db.py dist\\
                    if exist clear_table.py copy clear_table.py dist\\
                    if exist requirements.txt copy requirements.txt dist\\
                '''
            }
        }
        
        stage('Archive Artifacts') {
            steps {
                echo 'Archiving build artifacts...'
                archiveArtifacts artifacts: 'dist/**/*', fingerprint: true
                archiveArtifacts artifacts: 'test-results.xml', allowEmptyArchive: true
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline execution completed!'
            junit testResults: 'test-results.xml', allowEmptyResults: true
        }
        success {
            echo '✓ Build successful!'
        }
        failure {
            echo '✗ Build failed! Check logs for details.'
        }
        unstable {
            echo '⚠ Build unstable. Review warnings and test failures.'
        }
    }
}
