
# -------------------- Extra Tabs for Delay Analysis --------------------
tab4, tab5, tab6 = st.tabs([
    "📄 Delay by Permit Type",
    "🔧 Delay by Job Type",
    "📈 Delay Over Time"
])

with tab4:
    st.subheader("📄 Average Delay by Permit Type")
    st.bar_chart(df.groupby("Permit Type")["Delay"].mean().sort_values())

with tab5:
    st.subheader("🔧 Average Delay by Job Type")
    st.bar_chart(df.groupby("Job Type")["Delay"].mean().sort_values())

with tab6:
    st.subheader("📈 Monthly Delay Trend")
    df['Month'] = df['Filing Date'].dt.to_period("M").astype(str)
    monthly_avg = df.groupby("Month")["Delay"].mean().sort_index()
    st.line_chart(monthly_avg)
