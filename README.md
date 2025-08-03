# ETL-Project
Indian Migration Data ETL Pipeline
ETL script to process Indian migration data and store it in AWS S3 and DynamoDB.
Prerequisites
•	Python 3.7+
•	AWS credentials

#Setup
*Clone repository
git clone <repository-url>
cd indian-migration-etl

*Configure AWS credentials
aws configure
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
*Run Pipeline
In the terminal go to the Project file and run 
python ETL.py

#Files Setup
•	ETL.py - Main ETL script
•	IndianMigrationHistory1.3.csv - Source data

