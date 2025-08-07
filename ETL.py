import pandas as pd
import boto3
import uuid
from botocore.exceptions import NoCredentialsError


# Extract Phase
def extract_data(file_path):
    try:
        df = pd.read_csv(file_path)
        print(" Data extracted successfully.")
        return df
    except Exception as e:
        print(f" Error extracting data: {e}")
        return None


# Transformation Phase
def transform_data(df):
    try:
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()


        expected_columns = ['firstname', 'lastname', 'bloodgroup']

        # Keep only relevant columns that exist
        available_columns = [col for col in expected_columns if col in df.columns]
        df = df[available_columns]

        # Clean the data
        # Remove leading/trailing whitespace
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()

        # Replace empty strings and 'nan' with None
        df = df.replace(['', 'nan', 'NaN', 'null'], None)

        # Create a unique identifier for each record
        df['RecordID'] = [str(uuid.uuid4()) for _ in range(len(df))]

        # Remove completely empty rows (where all main fields are None/empty)
        df_cleaned = df.dropna(how='all', subset=['firstname', 'lastname', 'bloodgroup'])

        # Standardize blood group format if present
        if 'bloodgroup' in df_cleaned.columns:
            df_cleaned['bloodgroup'] = df_cleaned['bloodgroup'].str.upper()

        print(f" Data transformed successfully. {len(df_cleaned)} records processed.")
        return df_cleaned
    except Exception as e:
        print(f" Error transforming data: {e}")
        return None


# Loading Phase: Upload to S3
def upload_to_s3(file_name, bucket, object_key):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(file_name, bucket, object_key)
        print(f" File uploaded to S3: s3://{bucket}/{object_key}")
    except FileNotFoundError:
        print(" File not found.")
    except NoCredentialsError:
        print(" AWS credentials not available.")
    except Exception as e:
        print(f" Failed to upload file to S3: {e}")


# Loading Phase: Insert into DynamoDB
def insert_into_dynamodb(table_name, df):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        successful_inserts = 0
        skipped = 0

        for _, row in df.iterrows():
            item = {
                'RecordID': str(row.get('RecordID', str(uuid.uuid4()))),
                'FirstName': str(row.get('firstname', '')).strip() if pd.notna(row.get('firstname')) else '',
                'LastName': str(row.get('lastname', '')).strip() if pd.notna(row.get('lastname')) else '',
                'BloodGroup': str(row.get('bloodgroup', '')).strip() if pd.notna(row.get('bloodgroup')) else ''
            }

            # Only insert if we have at least one non-empty field besides RecordID
            if any([item['FirstName'], item['LastName'], item['BloodGroup']]):
                try:
                    table.put_item(Item=item)
                    successful_inserts += 1
                except Exception as e:
                    print(f" Error inserting record {item['RecordID']}: {e}")
                    skipped += 1
            else:
                skipped += 1
                print(f" Skipping row due to all empty fields: {item['RecordID']}")

        print(f" Data inserted into DynamoDB. {successful_inserts} successful inserts, {skipped} skipped rows.")
    except Exception as e:
        print(f"Error inserting into DynamoDB: {e}")


# Data validation function
def validate_data(df):
    print("\n Data Summary:")
    print(f"Total records: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    for col in df.columns:
        if col != 'RecordID':
            non_null_count = df[col].notna().sum()
            print(f"{col}: {non_null_count} non-null values")

    # Show unique blood groups if available
    if 'bloodgroup' in df.columns:
        unique_blood_groups = df['bloodgroup'].dropna().unique()
        print(f"Unique blood groups: {unique_blood_groups}")


# Main Execution
if __name__ == "__main__":
    file_path = "random dataset - Sheet1 (1).csv"
    df = extract_data(file_path)

    if df is not None:
        df_cleaned = transform_data(df)
        if df_cleaned is not None:
            # Validate and show data summary
            validate_data(df_cleaned)

            # Save cleaned data
            cleaned_file = "cleaned_personal_data.csv"
            df_cleaned.to_csv(cleaned_file, index=False)
            print(f" Cleaned data saved to {cleaned_file}")

            # Upload to S3
            bucket_name = "indian-migration-data-bucket"
            s3_key = "cleaned_data/cleaned_personal_data.csv"
            upload_to_s3(cleaned_file, bucket_name, s3_key)

            # Insert into DynamoDB
            dynamodb_table = "MigrationRecords"
            insert_into_dynamodb(dynamodb_table, df_cleaned)