import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io

# 1. GITHUB RAW URL CONFIGURATION - LÜTFEN RAW LİNKLERİ GÜNCELLEYİN
GITHUB_CSV_URL = "https://raw.githubusercontent.com/twidinebandm/sm-analysis-tool/refs/heads/main/yaya.csv"

# Logoyu GitHub'a yükleyip Raw linkini buraya yapıştırın.
GITHUB_LOGO_URL = "https://raw.githubusercontent.com/twidinebandm/sm-analysis-tool/refs/heads/main/CONCEPT_LOGO%20(1)_beyaz.png"

# Page Configuration
st.set_page_config(page_title="Concept Istanbul Social Media Analytics Tool", layout="wide")

# --- UNICODE SAFE PDF CLASS WITH LOGO AND DASHBOARD METRICS ---
class SafePDF(FPDF):
    def header(self):
        # Add Logo to PDF from GitHub
        try:
            # FPDF can't read from URL, so we pass image bytes later in create_visual_pdf
            if hasattr(self, 'logo_bytes'):
                self.image(self.logo_bytes, x=80, y=10, w=50) # Cetered, W=50mm
                self.ln(25) # Space after logo
        except:
            pass # Skip logo if error, text header will show

        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Social Media Performance Visual Report", ln=True, align="C")
        self.ln(5)

    def safe_text(self, text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

def create_visual_pdf(df, stats, figs, logo_bytes):
    pdf = SafePDF()
    # Pass logo bytes to PDF class before creating pages
    pdf.logo_bytes = io.BytesIO(logo_bytes) if logo_bytes else None
    
    # --- PAGE 1: Metrics & First 2 Charts ---
    pdf.add_page()
    
    # Header Section: Summary Metrics (Colorful)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Executive Summary Metrics", ln=True)
    pdf.set_font("Helvetica", "", 11)
    
    # PDF'e metrikleri yan yana renkli kutucuklar halinde ekle
    pdf.cell(60, 10, f"Total Impressions: {stats['imp']:,.0f}", border=1)
    pdf.cell(60, 10, f"Total Engagement: {stats['eng']:,.0f}", border=1)
    pdf.cell(60, 10, f"Total Contents: {stats['cnt']}", border=1)
    pdf.ln(15)

    # Chart 1: Impression Share by Platform
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "1. Impression Share by Platform", ln=True)
    img_bytes1 = figs[0].to_image(format="png", width=800, height=450)
    pdf.image(io.BytesIO(img_bytes1), x=10, y=None, w=180)
    pdf.ln(10)

    # Chart 2: Top 10 Owners by Engagement
    pdf.cell(0, 10, "2. Top 10 Owners by Engagement", ln=True)
    img_bytes2 = figs[1].to_image(format="png", width=800, height=450)
    pdf.image(io.BytesIO(img_bytes2), x=10, y=None, w=180)
    
    # --- PAGE 2: Last 2 Charts ---
    pdf.add_page()
    
    # Chart 3: Top 10 Content Owners by Impressions
    pdf.cell(0, 10, "3. Top 10 Content Owners by Impressions", ln=True)
    img_bytes3 = figs[2].to_image(format="png", width=800, height=450)
    pdf.image(io.BytesIO(img_bytes3), x=10, y=None, w=180)
    pdf.ln(10)

    # Chart 4: Top 10 Accounts by Follower Count
    pdf.cell(0, 10, "4. Top 10 Accounts by Follower Count", ln=True)
    img_bytes4 = figs[3].to_image(format="png", width=800, height=450)
    pdf.image(io.BytesIO(img_bytes4), x=10, y=None, w=180)
    
    return bytes(pdf.output())

# --- DATA PROCESSING ---
def process_data(df):
    df.columns = [c.strip() for c in df.columns]
    df['Follower'] = pd.to_numeric(df['Follower'], errors='coerce').fillna(0)
    df['Engagement'] = pd.to_numeric(df['Engagement'], errors='coerce').fillna(0)
    df['Calculated_Impression'] = pd.to_numeric(df.get('Average Impression', 0), errors='coerce').fillna(0)
    df['Owner'] = df['Name'].fillna(df['Medium']) if 'Name' in df.columns else df['Medium']
    return df

# --- MAIN APP LAYOUT ---
# Header: Logo & Title
col_logo, col_title = st.columns([1, 4]) # Centering logic
with col_title:
    try:
        # Load and Display Logo from GitHub above the title
        st.image(GITHUB_LOGO_URL, width=200) 
    except:
        pass # Skip logo if error fetching from URL

    st.title("Social Media Analytics Tool")

try:
    # Veriyi GitHub'dan Çek
    df_raw = pd.read_csv(GITHUB_CSV_URL)
    df = process_data(df_raw)
    
    # Metrik Hazırlığı
    stats = {
        'imp': df['Calculated_Impression'].sum(),
        'eng': df['Engagement'].sum(),
        'cnt': len(df)
    }

    # GRAFİKLER
    # 1. Impression Share by Platform
    platform_data = df.groupby('Medium')['Calculated_Impression'].sum().reset_index()
    fig1 = px.pie(platform_data, values='Calculated_Impression', names='Medium', hole=0.4, 
                  title="Impression Share by Platform", color_discrete_sequence=px.colors.qualitative.Bold)
    
    # 2. Top 10 Owners by Engagement
    owner_eng = df.groupby('Owner')['Engagement'].sum().nlargest(10).reset_index()
    fig2 = px.bar(owner_eng, x='Engagement', y='Owner', orientation='h', 
                  title="Top 10 Owners by Engagement", color='Owner', color_discrete_sequence=px.colors.qualitative.Pastel)
    fig2.update_layout(yaxis={'categoryorder':'total ascending'})
    
    # 3. Top 10 Content Owners by Impressions
    owner_imp = df.groupby('Owner')['Calculated_Impression'].sum().nlargest(10).reset_index()
    fig3 = px.bar(owner_imp, x='Calculated_Impression', y='Owner', orientation='h', 
                  title="Top 10 Content Owners by Impressions", color='Owner', color_discrete_sequence=px.colors.sequential.Viridis)
    fig3.update_layout(yaxis={'categoryorder':'total ascending'})
    
    # 4. Top 10 Accounts by Follower Count
    owner_fol = df.groupby('Owner')['Follower'].max().nlargest(10).reset_index()
    fig4 = px.bar(owner_fol, x='Follower', y='Owner', orientation='h', 
                  title="Top 10 Accounts by Follower Count", color='Follower')
    fig4.update_layout(yaxis={'categoryorder':'total ascending'})

    # SIDEBAR EXPORT
    st.sidebar.header("Export Options")
    if st.sidebar.button("Generate Color PDF Report"):
        with st.spinner("Preparing charts and generating PDF..."):
            # We need to fetch logo bytes for PDF (FPDF doesn't handle URL images directly)
            import requests
            try:
                logo_response = requests.get(GITHUB_LOGO_URL)
                logo_bytes = logo_response.content
            except:
                logo_bytes = None # Proceed without logo if fetch error

            pdf_bytes = create_visual_pdf(df, stats, [fig1, fig2, fig3, fig4], logo_bytes)
            st.sidebar.download_button(
                label="⬇️ Download Visual PDF",
                data=pdf_bytes,
                file_name="Visual_Social_Media_Report.pdf",
                mime="application/pdf"
            )

    # WEB DISPLAY
    # Kutucuklar içinde metrikler
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Impressions", f"{stats['imp']:,.0f}")
    m2.metric("Total Engagement", f"{stats['eng']:,.0f}")
    m3.metric("Contents", stats['cnt'])

    st.divider()
    # Grafikler yan yana
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1, use_container_width=True)
    col2.plotly_chart(fig2, use_container_width=True)
    
    st.divider()
    col3, col4 = st.columns(2)
    col3.plotly_chart(fig3, use_container_width=True)
    col4.plotly_chart(fig4, use_container_width=True)
    
    # En alttaki veri tablosu
    st.divider()
    st.subheader("📋 Detailed Content Data Table")
    st.dataframe(df.drop(columns=['Calculated_Impression', 'Owner'], errors='ignore'), use_container_width=True)

except Exception as e:
    st.error(f"Application Error: {e}")
