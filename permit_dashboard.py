
import pandas as pd
import streamlit as st
import plotly.express as px

# Load data
df = pd.read_csv("../data/cleaned_full_permit_data.csv", parse_dates=["Filing Date", "Issuance Date"])

# Filter invalid coordinates
df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])
df = df[df['Delay'].between(1, 180)]

st.title("NYC Construction Permit Delay Dashboard")

# Date range filter
min_date = df['Filing Date'].min()
max_date = df['Filing Date'].max()

start_date, end_date = st.slider(
    "Select Filing Date Range:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

df = df[(df['Filing Date'] >= start_date) & (df['Filing Date'] <= end_date)]

# Permit type filter
permit_types = df['Permit Type'].unique().tolist()
selected_types = st.multiselect(
    "Select Permit Types:",
    options=permit_types,
    default=permit_types
)

df = df[df['Permit Type'].isin(selected_types)]

# Hover info
df['hover'] = df['BOROUGH'] + "<br>Permit: " + df['Permit Type'] + "<br>Delay: " + df['Delay'].astype(str) + " days"

# Plot interactive map
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
    title="Filtered NYC Permit Delay Map"
)

fig.update_layout(mapbox_style="carto-positron")
fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

st.plotly_chart(fig, use_container_width=True)
