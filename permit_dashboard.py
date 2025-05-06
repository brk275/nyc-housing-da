import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os

# -------------------- Page Config --------------------
st.set_page_config(page_title="NYC Permit Delay Dashboard", layout="wide")

# -------------------- Theme Detection --------------------
def detect_current_theme():
    try:
        with open('.streamlit/config.toml', 'r') as f:
            for line in f.readlines():
                if 'base =' in line:
                    return line.split('=')[1].strip().strip('"')
    except:
        return 'dark'

if 'theme' not in st.session_state:
    st.session_state.theme = detect_current_theme()

# -------------------- Theme Toggle --------------------
def switch_theme():
    new_theme = 'light' if st.session_state.theme == 'dark' else 'dark'
    config = f"""
[theme]
base = "{new_theme}"
primaryColor = "#4F8A8B"
backgroundColor = "{('#F9F9F9' if new_theme == 'light' else '#121212')}"
secondaryBackgroundColor = "{('#E6ECEF' if new_theme == 'light' else '#1E1E1E')}"
textColor = "{('#000000' if new_theme == 'light' else '#F4F4F4')}"
font = "sans serif"
"""
    os.makedirs('.streamlit', exist_ok=True)
    with open('.streamlit/config.toml', 'w') as f:
        f.write(config)
    st.session_state.theme = new_theme
    st.warning("🔁 Theme changed. Please refresh the page manually to apply changes.")

# -------------------- Header UI --------------------
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
    }
    .stButton>button {
        border-radius: 8px;
        border: 1px solid #ccc;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏗️ NYC Construction Permit Delay Dashboard")

top_row = st.columns([10, 1], gap="small")
with top_row[1]:
    toggle_label = "🌞 Dark/Light" if st.session_state.theme == 'light' else "🌗 Light/Dark"
    if st.button(toggle_label):
        switch_theme()

# -------------------- Load Data --------------------
with st.spinner("Loading data..."):
    try:
        # Load from relative path
        df = pd.read_csv(
            os.path.join("sample_5001_rows.csv"),
            parse_dates=["Filing Date", "Issuance Date"],
            low_memory=False
        )
        rowcount = len(df)
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        st.stop()

# -------------------- Preprocessing --------------------
df['Filing Date'] = pd.to_datetime(df['Filing Date'], errors='coerce')
df['Issuance Date'] = pd.to_datetime(df['Issuance Date'], errors='coerce')
df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])
df = df[df['Delay'].between(1, 180)]

def safe_col(name):
    return name if name in df.columns else None

desc_col = safe_col('Job Description')
permittee_col = safe_col("Permittee's Business Name")
owner_col = safe_col("Owner's Business Name")
job_num_col = safe_col('Job #')
cost_col = safe_col('Estimated Job Cost')

if desc_col:
    df[desc_col] = df[desc_col].astype(str).str.slice(0, 100) + "..."
else:
    df['Job Description Tooltip'] = "N/A"
    desc_col = 'Job Description Tooltip'

# -------------------- Filters --------------------
st.subheader("📅 Date & Permit Filters")
col1, col2 = st.columns(2)

with col1:
    min_date = df['Filing Date'].min().to_pydatetime().date()
    max_date = df['Filing Date'].max().to_pydatetime().date()
    start_date, end_date = st.slider("Select Filing Date Range:", min_value=min_date, max_value=max_date, value=(min_date, max_date))

with col2:
    permit_types = df['Permit Type'].unique().tolist()
    selected_types = st.multiselect("Select Permit Types:", options=permit_types, default=permit_types)

df = df[
    (df['Filing Date'] >= pd.to_datetime(start_date)) &
    (df['Filing Date'] <= pd.to_datetime(end_date)) &
    (df['Permit Type'].isin(selected_types))
]
#--------------------- Limit for Performance --------------------
if len(df) > 5000:
    df = df.sample(n=5000, random_state=42)
    st.info("📦 Displaying 5,000-row sample for performance.")

# -------------------- Hover Text --------------------
df['hover'] = (
    "<b>Borough:</b> " + df['BOROUGH'].astype(str) + "<br>" +
    "<b>Permit:</b> " + df['Permit Type'].astype(str) +
    " | <b>Job:</b> " + df.get('Job Type', pd.Series("N/A", index=df.index)).astype(str) + "<br>" +
    "<b>Filed:</b> " + df['Filing Date'].astype(str) + "<br>" +
    "<b>Issued:</b> " + df['Issuance Date'].astype(str) + "<br>" +
    "<b>Delay:</b> " + df['Delay'].astype(str) + " days<br>" +
    ("<b>Job #:</b> " + df[job_num_col].astype(str) + "<br>" if job_num_col else "") +
    ("<b>Permittee:</b> " + df[permittee_col].astype(str) + "<br>" if permittee_col else "") +
    ("<b>Owner:</b> " + df[owner_col].astype(str) + "<br>" if owner_col else "")
)

# -------------------- Map and Tabs --------------------
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
fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

tab1, tab2, tab3 = st.tabs(["🗺️ Map", "📊 Delay by Borough", "📥 Export"])

with tab1:
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("📌 Summary Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", f"{len(df):,}")
    col2.metric("Avg Delay", f"{df['Delay'].mean():.1f} days")
    if cost_col:
        col3.metric("Total Est. Cost", f"${df[cost_col].dropna().astype(float).sum():,.0f}")

with tab2:
    st.subheader("📊 Average Delay by Borough")
    st.bar_chart(df.groupby("BOROUGH")["Delay"].mean().sort_values())

with tab3:
    st.subheader("📥 Download Filtered Data")
    st.download_button(
        label="Download CSV",
        data=df.to_csv(index=False),
        file_name="filtered_permit_data.csv",
        mime="text/csv"
    )

# -------------------- Advanced Filters --------------------
st.subheader("🛠️ Advanced Filters")
boroughs = sorted(df['BOROUGH'].dropna().unique())
selected_boroughs = st.multiselect("Filter by Borough:", options=boroughs, default=boroughs)
owner_query = st.text_input("Search Owner Name (all words, any order):")
permittee_query = st.text_input("Search Permittee Name (all words, any order):")

df = df[df['BOROUGH'].isin(selected_boroughs)]

if owner_query.strip() and owner_col:
    terms = owner_query.lower().split()
    df = df[df[owner_col].astype(str).str.lower().apply(lambda val: all(term in val for term in terms))]

if permittee_query.strip() and permittee_col:
    terms = permittee_query.lower().split()
    df = df[df[permittee_col].astype(str).str.lower().apply(lambda val: all(term in val for term in terms))]

# -------------------- Debug Info --------------------
with st.expander("🧪 Debug Info"):
    st.text(f"Loaded: {rowcount:,} rows | Filtered: {len(df):,} rows")
    st.text(f"Dates: {start_date} → {end_date}")
    st.text(f"Permit types: {', '.join(selected_types)}")
    st.write("🔍 Columns in dataset:", df.columns.tolist())
