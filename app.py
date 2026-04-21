import streamlit as st
import pandas as pd
import plotly.express as px

# 1. GITHUB RAW URL CONFIGURATION
# GitHub'daki dosyanıza gidin, "Raw" butonuna basın ve tarayıcıdaki URL'yi buraya yapıştırın.
GITHUB_CSV_URL = "https://github.com/twidinebandm/sm-analysis-tool/blob/550c9f3689c36c6e469e5e85288e956d0f73aeae/Yaya%20Gec%CC%A7idi%20SM%20I%CC%87c%CC%A7erikleri%20-%20Sheet1.csv"

# Page Configuration
st.set_page_config(page_title="Social Media Analytics Tool", layout="wide")

def process_data(df):
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    
    # Ensure numeric columns
    df['Follower'] = pd.to_numeric(df['Follower'], errors='coerce').fillna(0)
    df['Engagement'] = pd.to_numeric(df['Engagement'], errors='coerce').fillna(0)
    
    # Primary source: Average Impression from your sheet
    if 'Average Impression' in df.columns:
        df['Calculated_Impression'] = pd.to_numeric(df['Average Impression'], errors='coerce').fillna(0)
    else:
        df['Calculated_Impression'] = 0
        
    # Owner Name from 'Name' column
    if 'Name' in df.columns:
        df['Owner'] = df['Name'].fillna('Unknown')
    else:
        df['Owner'] = df['Medium'].astype(str)

    return df

# UI Header
st.title("📊 Social Media Performance Dashboard")
st.info(f"Data is being fetched automatically from GitHub.")

try:
    # AUTOMATIC FETCHING
    df_raw = pd.read_csv(GITHUB_CSV_URL)
    df = process_data(df_raw)
    
    # --- TOP METRICS ---
    total_imp = df['Calculated_Impression'].sum()
    total_eng = df['Engagement'].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Impressions", f"{total_imp:,.0f}")
    m2.metric("Total Engagement", f"{total_eng:,.0f}")
    m3.metric("Total Contents", len(df))

    st.divider()

    # --- CHARTS ---
    col_row1_1, col_row1_2 = st.columns(2)
    with col_row1_1:
        st.subheader("Impression Share by Platform")
        platform_imp = df.groupby('Medium')['Calculated_Impression'].sum().reset_index()
        fig1 = px.pie(platform_imp, values='Calculated_Impression', names='Medium', hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)

    with col_row1_2:
        st.subheader("Top 10 Content Owners by Engagement")
        owner_eng = df.groupby('Owner')['Engagement'].sum().nlargest(10).reset_index()
        fig2 = px.bar(owner_eng, x='Engagement', y='Owner', orientation='h', color='Owner')
        st.plotly_chart(fig2, use_container_width=True)

    col_row2_1, col_row2_2 = st.columns(2)
    with col_row2_1:
        st.subheader("Top 10 Content Owners by Impressions")
        owner_imp = df.groupby('Owner')['Calculated_Impression'].sum().nlargest(10).reset_index()
        fig3 = px.bar(owner_imp, x='Calculated_Impression', y='Owner', orientation='h', color='Owner')
        st.plotly_chart(fig3, use_container_width=True)

    with col_row2_2:
        st.subheader("Top 10 Accounts by Follower Count")
        owner_fol = df.groupby('Owner')['Follower'].max().nlargest(10).reset_index()
        fig4 = px.bar(owner_fol, x='Follower', y='Owner', orientation='h', color='Follower')
        st.plotly_chart(fig4, use_container_width=True)

    # --- DATA TABLE ---
    with st.expander("View Raw Data Table"):
        st.dataframe(df[['Owner', 'Medium', 'Follower', 'Engagement', 'Calculated_Impression', 'Link']], use_container_width=True)

except Exception as e:
    st.error(f"Error fetching data from GitHub: {e}")
    st.warning("Please check if the GITHUB_CSV_URL is correct and the file is public.")
