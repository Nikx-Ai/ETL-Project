pipeline {
  agent any

  environment {
    IMAGE = 'leo0011/etlproject1:latest'
  }

  stages {
    stage('Clone GitHub Repo') {
      steps {
        git url: 'https://github.com/Nikx-Ai/ETL-Project.git', branch: 'main'
      }
    }

    stage('Build Docker Image') {
      steps {
        sh 'docker build -t $IMAGE .'
      }
    }

    stage('Run ETL Job in Container') {
      steps {
        sh 'docker run --rm $IMAGE'
      }
    }

    stage('Push Image to DockerHub') {
      steps {
        withDockerRegistry([credentialsId: 'dockerhub-creds', url: '']) {
          sh 'docker push $IMAGE'
        }
      }
    }
  }

  post {
    success {
      echo '✅ ETL pipeline completed and image pushed successfully!'
    }
    failure {
      echo '❌ Pipeline failed. Check console logs.'
    }
  }
}
