import pandas as pd
import os

# === Extract Phase ===
def extract_data(file_path):
    print("Extracting raw migration data from local file...")

    if not os.path.exists(file_path):
        print(f" File not found at: {file_path}")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        print("Data extracted successfully.")
        return df
    except Exception as e:
        print("Failed to read the CSV file:", e)
        return pd.DataFrame()

# === Transform Phase ===
def transform_data(df):
    print(" Transforming data...")

    if df.empty:
        print(" No data to transform.")
        return df

    print(" Original columns:", df.columns.tolist())

    # Droping rows with missing values
    df_clean = df.dropna()

    # Example transformations 
    df_clean = df_clean.rename(columns={
        'State of Origin': 'Origin_State',
        'State of Destination': 'Destination_State',
        'Year': 'Migration_Year'
    }) if 'State of Origin' in df.columns else df_clean

    if 'Migration_Year' in df_clean.columns:
        df_clean['Migration_Year'] = df_clean['Migration_Year'].astype(int)
        df_clean = df_clean[df_clean['Migration_Year'] >= 2000]  

    # Remove duplicates
    df_clean = df_clean.drop_duplicates()

    print(" Data transformation complete.")
    return df_clean

# === Load Phase ===
def load_data(df_clean, output_path="cleaned_indian_migration.csv"):
    if df_clean.empty:
        print(" No data to save.")
        return
    print(f" Saving cleaned data to {output_path}...")
    df_clean.to_csv(output_path, index=False)
    print("✅ Data saved successfully.")

# === Main Execution ===
def main():
    file_path = r"C:\Users\Hp\OneDrive\Desktop\archive (3)\IndianMigrationHistory1.3.csv"
    raw_df = extract_data(file_path)
    cleaned_df = transform_data(raw_df)
    load_data(cleaned_df)

if __name__ == "__main__":
    main()
