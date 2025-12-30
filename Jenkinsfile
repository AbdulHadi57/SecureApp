/*
 * ========================================
 * Jenkins CI/CD Pipeline for Flask App
 * ========================================
 * 
 * Student Name: Abdul Hadi
 * Roll Number:  22i-1693
 * 
 * Repository: https://github.com/AbdulHadi57/SecureApp
 * Purpose: Automated build, test, and deployment pipeline
 * 
 * ========================================
 */

pipeline {
    agent any
    
    environment {
        // Environment Variables
        FLASK_APP = 'app.py'
        FLASK_ENV = 'development'
        DEPLOYMENT_DIR = 'C:\\deployment\\SecureApp'
        PYTHON_VERSION = 'python'
        VENV_DIR = 'venv'
        
        // Student Information
        STUDENT_NAME = 'Abdul Hadi'
        ROLL_NUMBER = '22i-1693'
    }
    
    stages {
        
        // ========================================
        // STAGE 1: Clone Repository
        // ========================================
        stage('Clone Repository') {
            steps {
                echo '========================================='
                echo 'STAGE 1: Cloning Repository'
                echo "Student: ${STUDENT_NAME} (${ROLL_NUMBER})"
                echo '========================================='
                
                // Clean workspace before cloning
                deleteDir()
                
                // Clone the Flask application repository from GitHub
                checkout([$class: 'GitSCM', branches: [[name: '*/main']], userRemoteConfigs: [[url: 'https://github.com/AbdulHadi57/SecureApp.git']]])
                
                echo '✓ Repository cloned successfully!'
            }
        }
        
        // ========================================
        // STAGE 2: Install Dependencies
        // ========================================
        stage('Install Dependencies') {
            steps {
                echo '========================================='
                echo 'STAGE 2: Installing Dependencies'
                echo '========================================='
                
                script {
                    if (isUnix()) {
                        // Linux/Unix commands
                        sh """
                            # Create Python virtual environment
                            ${PYTHON_VERSION} -m venv ${VENV_DIR}
                            . ${VENV_DIR}/bin/activate
                            
                            # Upgrade pip
                            pip install --upgrade pip
                            
                            # Install dependencies from requirements.txt
                            pip install -r requirements.txt
                        """
                    } else {
                        // Windows commands
                        bat """
                            REM Create Python virtual environment
                            ${PYTHON_VERSION} -m venv ${VENV_DIR}
                            call ${VENV_DIR}\\Scripts\\activate.bat
                            
                            REM Upgrade pip
                            python -m pip install --upgrade pip
                            
                            REM Install dependencies from requirements.txt
                            pip install -r requirements.txt
                        """
                    }
                }
                
                echo '✓ Dependencies installed successfully!'
            }
        }
        
        // ========================================
        // STAGE 3: Run Unit Tests
        // ========================================
        stage('Run Unit Tests') {
            steps {
                echo '========================================='
                echo 'STAGE 3: Running Unit Tests'
                echo '========================================='
                
                script {
                    if (isUnix()) {
                        sh """
                            . ${VENV_DIR}/bin/activate
                            pytest --verbose --junit-xml=test-results.xml --cov=. --cov-report=xml --cov-report=html
                        """
                    } else {
                        bat """
                            call ${VENV_DIR}\\Scripts\\activate.bat
                            pytest --verbose --junit-xml=test-results.xml --cov=. --cov-report=xml --cov-report=html
                        """
                    }
                }
                
                echo '✓ Unit tests completed successfully!'
            }
            post {
                always {
                    // Publish test results to Jenkins
                    junit 'test-results.xml'

                }
                failure {
                    echo '✗ Unit tests failed! Please review the test results.'
                }
            }
        }
        
        // ========================================
        // STAGE 4: Build Application
        // ========================================
        stage('Build Application') {
            steps {
                echo '========================================='
                echo 'STAGE 4: Building Application'
                echo '========================================='
                
                script {
                    if (isUnix()) {
                        sh """
                            . ${VENV_DIR}/bin/activate
                            
                            # Initialize the database
                            python create_db.py || true
                            
                            # Create build directory
                            mkdir -p build
                            
                            # Copy application files to build directory
                            cp -r app.py requirements.txt templates instance build/ || true
                            cp -r ${VENV_DIR} build/ || true
                            
                            # Create build information file
                            echo "Build Number: ${BUILD_NUMBER}" > build/build-info.txt
                            echo "Build Date: \$(date)" >> build/build-info.txt
                            echo "Git Commit: ${GIT_COMMIT}" >> build/build-info.txt
                            echo "Student: ${STUDENT_NAME}" >> build/build-info.txt
                            echo "Roll Number: ${ROLL_NUMBER}" >> build/build-info.txt
                        """
                    } else {
                        bat """
                            call ${VENV_DIR}\\Scripts\\activate.bat
                            
                            REM Initialize the database
                            python create_db.py || exit /b 0
                            
                            REM Create build directory
                            if not exist build mkdir build
                            
                            REM Copy application files to build directory
                            xcopy /Y /I app.py build\\
                            xcopy /Y /I requirements.txt build\\
                            xcopy /E /I /Y templates build\\templates\\
                            xcopy /E /I /Y instance build\\instance\\
                            
                            REM Create build information file
                            echo Build Number: ${BUILD_NUMBER} > build\\build-info.txt
                            echo Build Date: %date% %time% >> build\\build-info.txt
                            echo Git Commit: ${GIT_COMMIT} >> build\\build-info.txt
                            echo Student: ${STUDENT_NAME} >> build\\build-info.txt
                            echo Roll Number: ${ROLL_NUMBER} >> build\\build-info.txt
                        """
                    }
                }
                
                echo '✓ Application build completed successfully!'
            }
            post {
                success {
                    // Archive the build artifacts
                    archiveArtifacts artifacts: 'build/**/*', fingerprint: true
                }
            }
        }
        
        // ========================================
        // STAGE 5: Deploy Application
        // ========================================
        stage('Deploy Application') {
            steps {
                echo '========================================='
                echo 'STAGE 5: Deploying Application'
                echo "Deploying to: ${DEPLOYMENT_DIR}"
                echo '========================================='
                
                script {
                    if (isUnix()) {
                        sh """
                            # Create deployment directory if it doesn't exist
                            mkdir -p ${DEPLOYMENT_DIR}
                            
                            # Stop any running Flask application
                            pkill -f "flask run" || true
                            pkill -f "${FLASK_APP}" || true
                            
                            # Copy build artifacts to deployment directory
                            cp -r build/* ${DEPLOYMENT_DIR}/
                            
                            # Set proper permissions
                            chmod -R 755 ${DEPLOYMENT_DIR}
                            
                            # Navigate to deployment directory and start application
                            cd ${DEPLOYMENT_DIR}
                            . ${VENV_DIR}/bin/activate
                            
                            # Start the Flask application in background
                            nohup python ${FLASK_APP} > app.log 2>&1 &
                            
                            echo "Application deployed and started successfully!"
                        """
                    } else {
                        bat """
                            REM Create deployment directory if it doesn't exist
                            if not exist ${DEPLOYMENT_DIR} mkdir ${DEPLOYMENT_DIR}
                            
                            REM Stop any running Flask application
                            taskkill /F /IM python.exe /FI "WINDOWTITLE eq Flask*" || exit /b 0
                            
                            REM Copy build artifacts to deployment directory
                            xcopy /E /I /Y build\\* ${DEPLOYMENT_DIR}\\
                            
                            REM Display deployment information
                            echo ========================================
                            echo Application deployed successfully!
                            echo Location: ${DEPLOYMENT_DIR}
                            echo Student: ${STUDENT_NAME}
                            echo Roll Number: ${ROLL_NUMBER}
                            echo ========================================
                            echo.
                            echo To start the application manually:
                            echo cd ${DEPLOYMENT_DIR}
                            echo call ${VENV_DIR}\\Scripts\\activate.bat
                            echo python ${FLASK_APP}
                        """
                    }
                }
                
                echo '✓ Deployment completed successfully!'
            }
        }
    }
    
    // ========================================
    // Post-build Actions
    // ========================================
    post {
        always {
            echo '========================================='
            echo 'Pipeline Execution Completed'
            echo "Student: ${STUDENT_NAME}"
            echo "Roll Number: ${ROLL_NUMBER}"
            echo '========================================='
        }
        success {
            echo '✓ SUCCESS: Pipeline completed successfully!'
            echo '✓ All stages passed'
            echo '✓ Application deployed and ready'
        }
        failure {
            echo '✗ FAILURE: Pipeline failed!'
            echo '✗ Please check the console output for errors'
        }
        unstable {
            echo '⚠ WARNING: Pipeline unstable'
            echo '⚠ Some tests may have failed'
        }
    }
}
