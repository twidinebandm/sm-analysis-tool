import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# GitHub CSV URL
GITHUB_CSV_URL = "https://raw.githubusercontent.com/twidinebandm/sm-analysis-tool/refs/heads/main/Yaya%20Gec%CC%A7idi%20SM%20I%CC%87c%CC%A7erikleri%20-%20Sheet1.csv"

st.set_page_config(page_title="Social Media Analytics Tool", layout="wide")

# --- UNICODE SAFE PDF CLASS ---
class SafePDF(FPDF):
    def safe_text(self, text):
        # Desteklenmeyen karakterleri temizler veya soru işaretine çevirir
        return str(text).encode('latin-1', 'replace').decode('latin-1')

def create_pdf(df, total_imp, total_eng):
    pdf = SafePDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, pdf.safe_text("Social Media Performance Report"), ln=True, align="C")
    pdf.ln(10)
    
    # Summary Metrics
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "1. Executive Summary", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 10, f"Total Impressions: {total_imp:,.0f}", ln=True)
    pdf.cell(0, 10, f"Total Engagement: {total_eng:,.0f}", ln=True)
    pdf.cell(0, 10, f"Total Contents: {len(df)}", ln=True)
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 10, "Owner Name", 1)
    pdf.cell(50, 10, "Impressions", 1)
    pdf.ln()
    
    # Data Rows
    pdf.set_font("Helvetica", "", 10)
    top_10_pdf = df.groupby('Owner')['Calculated_Impression'].sum().nlargest(10).reset_index()
    
    for _, row in top_10_pdf.iterrows():
        owner_name = pdf.safe_text(row['Owner'])
        pdf.cell(90, 10, owner_name[:45], 1) 
        pdf.cell(50, 10, f"{row['Calculated_Impression']:,.0f}", 1)
        pdf.ln()
        
    # HATA DÜZELTMESİ: bytearray nesnesini bytes tipine dönüştürüyoruz
    return bytes(pdf.output())

# --- DATA PROCESSING ---
def process_data(df):
    df.columns = [c.strip() for c in df.columns]
    df['Follower'] = pd.to_numeric(df['Follower'], errors='coerce').fillna(0)
    df['Engagement'] = pd.to_numeric(df['Engagement'], errors='coerce').fillna(0)
    
    if 'Average Impression' in df.columns:
        df['Calculated_Impression'] = pd.to_numeric(df['Average Impression'], errors='coerce').fillna(0)
    else:
        df['Calculated_Impression'] = 0
        
    if 'Name' in df.columns:
        df['Owner'] = df['Name'].fillna(df['Medium'])
    else:
        df['Owner'] = df['Medium']
    return df

# --- MAIN APP ---
st.title("📊 Social Media Performance Dashboard")

try:
    # GitHub'dan veriyi çek
    df_raw = pd.read_csv(GITHUB_CSV_URL)
    df = process_data(df_raw)
    
    total_imp = df['Calculated_Impression'].sum()
    total_eng = df['Engagement'].sum()

    # Sidebar Export Section
    st.sidebar.header("Report Export")
    
    # PDF oluşturma işlemini değişkene atayarak kontrol ediyoruz
    try:
        # PDF verisini oluştur
        pdf_output = create_pdf(df, total_imp, total_eng)
        
        st.sidebar.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_output,
            file_name="SM_Performance_Report.pdf",
            mime="application/pdf"
        )
    except Exception as pdf_err:
        st.sidebar.error(f"PDF Generation Error: {pdf_err}")

    # Dashboard Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Impressions", f"{total_imp:,.0f}")
    m2.metric("Total Engagement", f"{total_eng:,.0f}")
    m3.metric("Total Contents", len(df))

    st.divider()

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Impression Share by Platform")
        fig1 = px.pie(df, values='Calculated_Impression', names='Medium', hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        st.subheader("Top 10 Owners by Engagement")
        owner_eng = df.groupby('Owner')['Engagement'].sum().nlargest(10).reset_index()
        fig2 = px.bar(owner_eng, x='Engagement', y='Owner', orientation='h')
        st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
