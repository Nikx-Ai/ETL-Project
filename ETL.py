import pandas as pd
import boto3
import uuid
from botocore.exceptions import NoCredentialsError

# Extract Phase
def extract_data(file_path):
    try:
        df = pd.read_csv(file_path)
        print("Data extracted successfully.")
        return df
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None

# Transformation Phase
def transform_data(df):
    try:
        df.columns = df.columns.str.strip()

        # Keep only relevant columns
        columns_to_keep = ['Country Dest Name'] + [col for col in df.columns if col.startswith('19') or col.startswith('20')]
        df = df[columns_to_keep]

        # Convert wide format to long format
        df_melted = df.melt(id_vars=['Country Dest Name'], var_name='Year', value_name='MigrationCount')

        # Rename columns to match DynamoDB schema
        df_melted.rename(columns={'Country Dest Name': 'State'}, inplace=True)

        # Remove rows with missing data
        df_melted.dropna(subset=['Year', 'State', 'MigrationCount'], inplace=True)

        # Remove invalid or placeholder values
        df_melted = df_melted[~df_melted['MigrationCount'].astype(str).isin(['', ' ', '..', 'NaN', 'nan'])]

        # Clean up and ensure string format
        df_melted['Year'] = df_melted['Year'].astype(str).str.extract(r'(\d{4})')[0]
        df_melted['State'] = df_melted['State'].astype(str).str.strip()
        df_melted['MigrationCount'] = df_melted['MigrationCount'].astype(str).str.strip()

        # Final drop of any rows with now-empty fields
        df_melted.dropna(subset=['Year', 'State', 'MigrationCount'], inplace=True)

        print("Data transformed successfully.")
        return df_melted
    except Exception as e:
        print(f"Error transforming data: {e}")
        return None

# Loading Phase: Upload to S3
def upload_to_s3(file_name, bucket, object_key):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(file_name, bucket, object_key)
        print(f"File uploaded to S3: s3://{bucket}/{object_key}")
    except FileNotFoundError:
        print("File not found.")
    except NoCredentialsError:
        print("AWS credentials not available.")
    except Exception as e:
        print(f"Failed to upload file to S3: {e}")

# Loading Phase: Insert into DynamoDB
def insert_into_dynamodb(table_name, df):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        skipped = 0
        for _, row in df.iterrows():
            item = {
                'RecordID': str(uuid.uuid4()),
                'Year': str(row.get('Year', '')).strip(),
                'State': str(row.get('State', '')).strip(),
                'MigrationCount': str(row.get('MigrationCount', '')).strip()
            }

            if item['Year'] and item['State'] and item['MigrationCount']:
                table.put_item(Item=item)
            else:
                skipped += 1
                print(f"Skipping row due to missing field(s): {item}")

        print(f"Data inserted into DynamoDB. Skipped {skipped} invalid rows.")
    except Exception as e:
        print(f"Error inserting into DynamoDB: {e}")

# Main Execution
if __name__ == "__main__":
    file_path = "IndianMigrationHistory1.3.csv"
    df = extract_data(file_path)

    if df is not None:
        df_cleaned = transform_data(df)
        if df_cleaned is not None:
            cleaned_file = "cleaned_indian_migration.csv"
            df_cleaned.to_csv(cleaned_file, index=False)

            bucket_name = "indian-migration-data-bucket"
            s3_key = "cleaned_data/cleaned_indian_migration.csv"
            upload_to_s3(cleaned_file, bucket_name, s3_key)

            dynamodb_table = "MigrationRecords"
            insert_into_dynamodb(dynamodb_table, df_cleaned)
