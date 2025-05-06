import pandas as pd

# Load the full CSV in chunks
input_path = r"DOB_Permit_Issuance_20250504.csv"
output_path = "cleaned_full_permit_data_v2.csv"
chunks = pd.read_csv(input_path, chunksize=100000, low_memory=False)

# Save full header sample for inspection
sample_row = pd.read_csv(input_path, nrows=1)
sample_row.to_csv("sample_header_preview.csv", index=False)
print("📝 Saved first row to 'sample_header_preview.csv' for column inspection.\n")
print("🔎 Column headers:")
print(sample_row.columns.tolist())

desired_cols = [
    'LATITUDE', 'LONGITUDE','BOROUGH', 'Permit Type', 'Job Type', 'Filing Date', 'Issuance Date', 'Permit Status',
    'Job #', "Owner's Business Name", "Permittee's Business Name", 'Job Description',
    'BIN', 'Block', 'Lot', 'Estimated Job Cost'
]

cleaned_chunks = []

for i, chunk in enumerate(chunks):
    print(f"Processing chunk {i + 1}...")

    # Normalize column names to handle casing/spacing
    original_columns = chunk.columns.tolist()
    column_map = {col.strip().lower(): col for col in original_columns}
    normalized_cols = [col.strip().lower() for col in original_columns]

    # Map desired lowercase col names to their original case
    valid_cols = [column_map[col.lower()] for col in desired_cols if col.lower() in column_map]
    chunk = chunk[valid_cols]

    # Rename columns to standard form if present
    col_renames = {
        "permittee's business name": 'Contractor Business Name'
    }
    chunk.rename(columns=col_renames, inplace=True)

    # Convert dates and calculate delay
    if 'Filing Date' in chunk.columns and 'Issuance Date' in chunk.columns:
        chunk['Filing Date'] = pd.to_datetime(chunk['Filing Date'], errors='coerce')
        chunk['Issuance Date'] = pd.to_datetime(chunk['Issuance Date'], errors='coerce')
        chunk['Delay'] = (chunk['Issuance Date'] - chunk['Filing Date']).dt.days

        chunk = chunk.dropna(subset=['Filing Date', 'Issuance Date', 'Delay', 'BOROUGH', 'Permit Type', 'Job Type'])
        chunk = chunk[chunk['Delay'].between(1, 180)]
    else:
        print("❌ Missing required date columns. Skipping chunk.")
        continue

    # Filter to issued permits
    if 'Permit Status' in chunk.columns:
        chunk = chunk[chunk['Permit Status'] == 'ISSUED']

    # Fill missing values
    chunk = chunk.fillna("N/A")

    cleaned_chunks.append(chunk)

# Concatenate and save
if cleaned_chunks:
    df_cleaned = pd.concat(cleaned_chunks)
    df_cleaned.to_csv(output_path, index=False)
    print(f"✅ Saved cleaned dataset to {output_path}")
else:
    print("⚠️ No valid data chunks to save.")
