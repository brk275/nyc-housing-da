import pandas as pd

# Load a small chunk for testing
df = pd.read_csv(r'C:\Users\Alex\Downloads\DOB_Permit_Issuance_20250504.csv', nrows=1000)

# Show all columns
print(df.columns)

# Check nulls
print(df.isnull().sum().sort_values(ascending=False))

# Quick sample rows
print(df.sample(5).T)

# Check unique values in key fields
print(df['Permit Type'].value_counts())
print(df['Borough'].value_counts())
print(df['Job Type'].value_counts())

# Check date formats
df['Filing Date'] = pd.to_datetime(df['Filing Date'], errors='coerce')
df['Issuance Date'] = pd.to_datetime(df['Issuance Date'], errors='coerce')
df['Delay'] = (df['Issuance Date'] - df['Filing Date']).dt.days

print(df['Delay'].describe())


print(df.columns.tolist())  # show all column names
print(df.sample(3).T)       # show 3 sample rows, transposed