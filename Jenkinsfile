pipeline {
    agent {
        docker {
            image 'python:3.10-slim'
            args '-u root'  // if permission issues
        }
    }
    environment {
        AWS_ACCESS_KEY_ID = credentials('your-aws-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('your-aws-secret-key')
    }
    stages {
        stage('Install Python Dependencies') {
            steps {
                sh 'pip install boto3 pandas'
            }
        }
        stage('Run ETL Pipeline') {
            steps {
                sh 'python ETL.py'
            }
        }
    }
    post {
        failure {
            echo '❌ ETL job failed. Check logs.'
        }
        success {
            echo '✅ ETL pipeline completed successfully.'
        }
    }
}

