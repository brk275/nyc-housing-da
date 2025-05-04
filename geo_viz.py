import pandas as pd
import plotly.express as px
import os

# Make sure the outputs directory exists
os.makedirs("../outputs", exist_ok=True)

# Load cleaned data
df = pd.read_csv(r"C:\Users\Alex\OneDrive\Documents\GitHub\nyc-housing-da\cleaned_full_permit_data.csv", low_memory=False)

# Drop rows with missing lat/lon
df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])

# Optional: Cap delay at 180 for color scale
df = df[df['Delay'].between(1, 180)]

# Create hover info
df['hover'] = df['BOROUGH'] + "<br>Permit: " + df['Permit Type'] + "<br>Delay: " + df['Delay'].astype(str) + " days"

# Plot
fig = px.scatter_mapbox(
    df,
    lat="LATITUDE",
    lon="LONGITUDE",
    color="Delay",
    color_continuous_scale="YlOrRd",
    size_max=5,
    zoom=10,
    height=600,
    hover_name="hover",
    title="NYC Permit Delay Heatmap"
)

fig.update_layout(mapbox_style="carto-positron")
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

# Save HTML output
fig.write_html("../outputs/nyc_permit_delay_map.html")
print("✅ Map saved to outputs/nyc_permit_delay_map.html")
