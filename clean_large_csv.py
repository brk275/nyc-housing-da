
import pandas as pd

# Load the full CSV in chunks (adjust 'chunksize' for memory limits)
chunks = pd.read_csv(r"C:\Users\Alex\Downloads\DOB_Permit_Issuance_20250504.csv", chunksize=3978542)

# Initialize an empty list to collect cleaned chunks
cleaned_chunks = []

for i, chunk in enumerate(chunks):
    print(f"Processing chunk {i + 1}...")
    
    # Drop columns with >90% missing values (only once, on the first chunk)
    if i == 0:
        valid_cols = chunk.loc[:, chunk.isnull().mean() < 0.9].columns
    chunk = chunk[valid_cols]

    # Convert date fields
    chunk['Filing Date'] = pd.to_datetime(chunk['Filing Date'], errors='coerce')
    chunk['Issuance Date'] = pd.to_datetime(chunk['Issuance Date'], errors='coerce')

    # Calculate delay
    chunk['Delay'] = (chunk['Issuance Date'] - chunk['Filing Date']).dt.days

    # Drop rows with invalid delays or missing key fields
    chunk = chunk.dropna(subset=['Filing Date', 'Issuance Date', 'Delay', 'BOROUGH', 'Permit Type', 'Job Type'])
    chunk = chunk[chunk['Delay'].between(1, 180)]

    # Optional: filter to only issued permits
    chunk = chunk[chunk['Permit Status'] == 'ISSUED']

    cleaned_chunks.append(chunk)

# Concatenate all cleaned chunks
df_cleaned = pd.concat(cleaned_chunks)

# Export to a new file
df_cleaned.to_csv("cleaned_full_permit_data.csv", index=False)

print("Cleaning complete. Rows in final dataset:", len(df_cleaned))
