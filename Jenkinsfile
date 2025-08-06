pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID = credentials('your-aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('your-aws-secret-access-key')
    }

    stages {
        stage('Install Python Dependencies') {
            steps {
                sh 'pip3 install --user boto3 pandas'
            }
        }

        stage('Run ETL Pipeline') {
            steps {
                sh 'python3 ETL.py'
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
