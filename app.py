import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(page_title="Social Media Analytics Tool", layout="wide")

def process_data(df):
    # Clean column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Ensure numeric columns are properly formatted
    df['Follower'] = pd.to_numeric(df['Follower'], errors='coerce').fillna(0)
    df['Engagement'] = pd.to_numeric(df['Engagement'], errors='coerce').fillna(0)
    
    # Primary source for impressions
    if 'Average Impression' in df.columns:
        df['Calculated_Impression'] = pd.to_numeric(df['Average Impression'], errors='coerce').fillna(0)
    else:
        df['Calculated_Impression'] = 0
        
    # Handle the "Owner" name from the 'Name' column
    if 'Name' in df.columns:
        df['Owner'] = df['Name'].fillna('Unknown')
    else:
        # If 'Name' column doesn't exist, use 'Medium' or 'Link' as fallback
        df['Owner'] = df['Medium'].astype(str)

    return df

# UI Header
st.title("📊 Social Media Performance Dashboard")
st.markdown("Metrics analyzed by Content Owners and Platforms")

uploaded_file = st.file_uploader("Upload your Social Media Data (CSV)", type="csv")

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file)
    df = process_data(df_raw)
    
    # --- TOP METRICS ---
    total_imp = df['Calculated_Impression'].sum()
    total_eng = df['Engagement'].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Impressions", f"{total_imp:,.0f}")
    m2.metric("Total Engagement", f"{total_eng:,.0f}")
    m3.metric("Total Contents", len(df))

    st.divider()

    # --- CHARTS SECTION ---
    
    # Row 1: Platform Share & Engagement Owners
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.subheader("Impression Share by Platform")
        platform_imp = df.groupby('Medium')['Calculated_Impression'].sum().reset_index()
        fig1 = px.pie(platform_imp, values='Calculated_Impression', names='Medium', hole=0.4,
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)

    with row1_col2:
        st.subheader("Top 10 Content Owners by Engagement")
        # Grouping by Owner to sum up multiple posts by same person
        owner_eng = df.groupby('Owner')['Engagement'].sum().nlargest(10).reset_index()
        fig2 = px.bar(owner_eng, x='Engagement', y='Owner', orientation='h', 
                      color='Owner', text_auto='.2s')
        fig2.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Row 2: Impression Owners & Follower Count
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Top 10 Content Owners by Impressions")
        owner_imp = df.groupby('Owner')['Calculated_Impression'].sum().nlargest(10).reset_index()
        fig3 = px.bar(owner_imp, x='Calculated_Impression', y='Owner', orientation='h',
                      color='Owner', text_auto='.2s')
        fig3.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig3, use_container_width=True)

    with row2_col2:
        st.subheader("Top 10 Accounts by Follower Count")
        # Using max follower count per owner
        owner_fol = df.groupby('Owner')['Follower'].max().nlargest(10).reset_index()
        fig4 = px.bar(owner_fol, x='Follower', y='Owner', orientation='h',
                      color='Follower', text_auto='.2s')
        fig4.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig4, use_container_width=True)

    # --- RAW DATA TABLE ---
    st.subheader("📋 Detailed Data View")
    st.dataframe(df[['Owner', 'Medium', 'Follower', 'Engagement', 'Calculated_Impression', 'Link']], use_container_width=True)

else:
    st.info("Please upload your CSV file to generate the visual report.")
