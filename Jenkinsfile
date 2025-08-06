pipeline {
    agent any

    environment {
        AWS_ACCESS_KEY_ID     = credentials('aws-access-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key')
        AWS_DEFAULT_REGION    = 'us-east-1'
    }

    stages {
        stage('Install Python Dependencies') {
            steps {
                sh 'pip3 install boto3 pandas'
            }
        }

        stage('Run ETL Pipeline') {
            steps {
                sh '''
                    export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                    export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
                    export AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION
                    python3 ETL.py
                '''
            }
        }
    }

    post {
        success {
            echo '✅ ETL job completed successfully!'
        }
        failure {
            echo '❌ ETL job failed. Check logs.'
        }
    }
}
