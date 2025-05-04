import pandas as pd

df_sample = pd.read_csv(r"C:\Users\Alex\Downloads\DOB_Permit_Issuance_20250504.csv", nrows=1000)

# Save it to a new file
df_sample.to_csv("sample_permit_data.csv", index=False)