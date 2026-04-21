import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io
from PIL import Image

# 1. CONFIGURATION
GITHUB_CSV_URL = "https://raw.githubusercontent.com/twidinebandm/sm-analysis-tool/refs/heads/main/Yaya%20Gec%CC%A7idi%20SM%20I%CC%87c%CC%A7erikleri%20-%20Sheet1.csv"

st.set_page_config(page_title="Social Media Analytics Tool", layout="wide")

# --- UNICODE SAFE PDF CLASS WITH IMAGE SUPPORT ---
class SafePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 15)
        self.cell(0, 10, "Social Media Performance Visual Report", ln=True, align="C")
        self.ln(5)

    def safe_text(self, text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

def create_pdf_with_charts(df, fig1, fig2, fig3, fig4):
    pdf = SafePDF()
    
    # --- PAGE 1: Summary & First 2 Charts ---
    pdf.add_page()
    
    # Section 1: Impression Share by Platform
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "1. Impression Share by Platform", ln=True)
    img_bytes1 = fig1.to_image(format="png", width=800, height=450)
    pdf.image(io.BytesIO(img_bytes1), x=10, y=None, w=180)
    pdf.ln(10)

    # Section 2: Top 10 Owners by Engagement
    pdf.cell(0, 10, "2. Top 10 Owners by Engagement", ln=True)
    img_bytes2 = fig2.to_image(format="png", width=800, height=450)
    pdf.image(io.BytesIO(img_bytes2), x=10, y=None, w=180)
    
    # --- PAGE 2: Last 2 Charts ---
    pdf.add_page()
    
    # Section 3: Top 10 Content Owners by Impressions
    pdf.cell(0, 10, "3. Top 10 Content Owners by Impressions", ln=True)
    img_bytes3 = fig3.to_image(format="png", width=800, height=450)
    pdf.image(io.BytesIO(img_bytes3), x=10, y=None, w=180)
    pdf.ln(10)

    # Section 4: Top 10 Accounts by Follower Count
    pdf.cell(0, 10, "4. Top 10 Accounts by Follower Count", ln=True)
    img_bytes4 = fig4.to_image(format="png", width=800, height=450)
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

# --- MAIN APP ---
st.title("📊 Social Media Visual Dashboard")

try:
    df_raw = pd.read_csv(GITHUB_CSV_URL)
    df = process_data(df_raw)

    # GRAPHIKS GENERATION (For both UI and PDF)
    # 1. Platform Share
    fig1 = px.pie(df, values='Calculated_Impression', names='Medium', hole=0.4)
    
    # 2. Top 10 Engagement
    owner_eng = df.groupby('Owner')['Engagement'].sum().nlargest(10).reset_index()
    fig2 = px.bar(owner_eng, x='Engagement', y='Owner', orientation='h', title="Top 10 by Engagement")
    
    # 3. Top 10 Impressions
    owner_imp = df.groupby('Owner')['Calculated_Impression'].sum().nlargest(10).reset_index()
    fig3 = px.bar(owner_imp, x='Calculated_Impression', y='Owner', orientation='h', title="Top 10 by Impressions")
    
    # 4. Top 10 Followers
    owner_fol = df.groupby('Owner')['Follower'].max().nlargest(10).reset_index()
    fig4 = px.bar(owner_fol, x='Follower', y='Owner', orientation='h', title="Top 10 by Followers")

    # SIDEBAR EXPORT
    st.sidebar.header("Export Options")
    if st.sidebar.button("Generate Visual PDF Report"):
        with st.spinner("Preparing charts and generating PDF..."):
            pdf_bytes = create_pdf_with_charts(df, fig1, fig2, fig3, fig4)
            st.sidebar.download_button(
                label="⬇️ Download Visual PDF",
                data=pdf_bytes,
                file_name="Visual_Social_Media_Report.pdf",
                mime="application/pdf"
            )

    # DISPLAY ON WEB
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Impressions", f"{df['Calculated_Impression'].sum():,.0f}")
    m2.metric("Total Engagement", f"{df['Engagement'].sum():,.0f}")
    m3.metric("Contents", len(df))

    st.divider()
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1, use_container_width=True)
    col2.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)
    col3.plotly_chart(fig3, use_container_width=True)
    col4.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
