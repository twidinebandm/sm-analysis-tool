import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# 1. CONFIGURATION
GITHUB_CSV_URL = "https://raw.githubusercontent.com/KULLANICI_ADINIZ/REPO_ADINIZ/main/Yaya_Gecidi_SM_Icerikleri.csv"

st.set_page_config(page_title="Social Media Analytics Tool", layout="wide")

# --- PDF GENERATION FUNCTION ---
def create_pdf(df, total_imp, total_eng):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Social Media Performance Report", ln=True, align="C")
    pdf.ln(10)
    
    # Summary Metrics
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Executive Summary", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Total Impressions: {total_imp:,.0f}", ln=True)
    pdf.cell(0, 10, f"Total Engagement: {total_eng:,.0f}", ln=True)
    pdf.cell(0, 10, f"Total Contents Analyzed: {len(df)}", ln=True)
    pdf.ln(10)
    
    # Top 10 by Impressions Table
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Top 10 Content Owners (by Impressions)", ln=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(80, 10, "Owner Name", 1)
    pdf.cell(50, 10, "Impressions", 1)
    pdf.ln()
    
    top_10_pdf = df.groupby('Owner')['Calculated_Impression'].sum().nlargest(10).reset_index()
    pdf.set_font("Arial", "", 10)
    for index, row in top_10_pdf.iterrows():
        pdf.cell(80, 10, str(row['Owner'])[:40], 1)
        pdf.cell(50, 10, f"{row['Calculated_Impression']:,.0f}", 1)
        pdf.ln()
        
    return pdf.output(dest="S").encode("latin-1", "replace")

# --- DATA PROCESSING ---
def process_data(df):
    df.columns = [c.strip() for c in df.columns]
    df['Follower'] = pd.to_numeric(df['Follower'], errors='coerce').fillna(0)
    df['Engagement'] = pd.to_numeric(df['Engagement'], errors='coerce').fillna(0)
    
    if 'Average Impression' in df.columns:
        df['Calculated_Impression'] = pd.to_numeric(df['Average Impression'], errors='coerce').fillna(0)
    else:
        df['Calculated_Impression'] = 0
        
    df['Owner'] = df['Name'].fillna(df['Medium']) if 'Name' in df.columns else df['Medium']
    return df

# --- MAIN APP ---
st.title("📊 Social Media Performance Dashboard")

try:
    df_raw = pd.read_csv(GITHUB_CSV_URL)
    df = process_data(df_raw)
    
    total_imp = df['Calculated_Impression'].sum()
    total_eng = df['Engagement'].sum()

    # SIDEBAR - EXPORT
    st.sidebar.header("Report Settings")
    if st.sidebar.button("Generate PDF Report"):
        pdf_bytes = create_pdf(df, total_imp, total_eng)
        st.sidebar.download_button(
            label="⬇️ Download PDF",
            data=pdf_bytes,
            file_name="Social_Media_Report.pdf",
            mime="application/pdf"
        )

    # METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Impressions", f"{total_imp:,.0f}")
    m2.metric("Total Engagement", f"{total_eng:,.0f}")
    m3.metric("Total Contents", len(df))

    st.divider()

    # CHARTS (Aynı kalıyor)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Impression Share by Platform")
        fig1 = px.pie(df, values='Calculated_Impression', names='Medium', hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.subheader("Top 10 Content Owners by Engagement")
        owner_eng = df.groupby('Owner')['Engagement'].sum().nlargest(10).reset_index()
        fig2 = px.bar(owner_eng, x='Engagement', y='Owner', orientation='h')
        st.plotly_chart(fig2, use_container_width=True)

    # DATA TABLE
    st.subheader("📋 Detailed Data View")
    st.dataframe(df[['Owner', 'Medium', 'Follower', 'Engagement', 'Calculated_Impression']], use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
