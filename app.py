import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io

# 1. CONFIGURATION
# GitHub'daki Raw CSV linkinizi buraya yapıştırın
GITHUB_CSV_URL = "https://raw.githubusercontent.com/twidinebandm/sm-analysis-tool/refs/heads/main/Yaya%20Gec%CC%A7idi%20SM%20I%CC%87c%CC%A7erikleri%20-%20Sheet1.csv"

st.set_page_config(page_title="Social Media Analytics Tool", layout="wide")

# --- UNICODE SAFE PDF CLASS ---
class SafePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Social Media Performance Report", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def safe_text(self, text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

def create_visual_pdf(df, stats, figs):
    pdf = SafePDF()
    
    # --- PAGE 1: Metrics & First 2 Charts ---
    pdf.add_page()
    
    # Summary Metrics Table
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Executive Summary Metrics", ln=True)
    pdf.set_font("Helvetica", "", 11)
    
    # Metrikleri PDF'e ekle
    pdf.cell(60, 10, f"Total Impressions: {stats['imp']:,.0f}", border=1)
    pdf.cell(60, 10, f"Total Engagement: {stats['eng']:,.0f}", border=1)
    pdf.cell(60, 10, f"Total Contents: {stats['cnt']}", border=1)
    pdf.ln(15)

    # Chart 1: Impression Share by Platform
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "1. Impression Share by Platform", ln=True)
    img_bytes1 = figs[0].to_image(format="png", width=800, height=450)
    pdf.image(io.BytesIO(img_bytes1), x=10, y=None, w=180)
    pdf.ln(5)

    # Chart 2: Top 10 Owners by Engagement
    pdf.cell(0, 10, "2. Top 10 Owners by Engagement", ln=True)
    img_bytes2 = figs[1].to_image(format="png", width=800, height=450)
    pdf.image(io.BytesIO(img_bytes2), x=10, y=None, w=180)
    
    # --- PAGE 2: Remaining Charts ---
    pdf.add_page()
    
    # Chart 3: Top 10 Content Owners by Impressions
    pdf.cell(0, 10, "3. Top 10 Content Owners by Impressions", ln=True)
    img_bytes3 = figs[2].to_image(format="png", width=800, height=450)
    pdf.image(io.BytesIO(img_bytes3), x=10, y=None, w=180)
    pdf.ln(5)

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
    # Use Average Impression from CSV
    df['Calculated_Impression'] = pd.to_numeric(df.get('Average Impression', 0), errors='coerce').fillna(0)
    # Set Owner from Name or Medium
    df['Owner'] = df['Name'].fillna(df['Medium']) if 'Name' in df.columns else df['Medium']
    return df

# --- APP LAYOUT ---
st.title("📊 Social Media Visual Analytics")

try:
    df_raw = pd.read_csv(GITHUB_CSV_URL)
    df = process_data(df_raw)

    # Stats for Metrics and PDF
    stats = {
        'imp': df['Calculated_Impression'].sum(),
        'eng': df['Engagement'].sum(),
        'cnt': len(df)
    }

    # 1. Impression Share by Platform
    platform_data = df.groupby('Medium')['Calculated_Impression'].sum().reset_index()
    fig1 = px.pie(platform_data, values='Calculated_Impression', names='Medium', 
                  title="Impression Share by Platform", hole=0.4,
                  color_discrete_sequence=px.colors.qualitative.Bold)

    # 2. Top 10 Owners by Engagement
    owner_eng = df.groupby('Owner')['Engagement'].sum().nlargest(10).reset_index()
    fig2 = px.bar(owner_eng, x='Engagement', y='Owner', orientation='h', 
                  title="Top 10 Owners by Engagement", color='Owner',
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig2.update_layout(yaxis={'categoryorder':'total ascending'})

    # 3. Top 10 Content Owners by Impressions
    owner_imp = df.groupby('Owner')['Calculated_Impression'].sum().nlargest(10).reset_index()
    fig3 = px.bar(owner_imp, x='Calculated_Impression', y='Owner', orientation='h', 
                  title="Top 10 Content Owners by Impressions", color='Owner',
                  color_discrete_sequence=px.colors.sequential.Viridis)
    fig3.update_layout(yaxis={'categoryorder':'total ascending'})

    # 4. Top 10 Accounts by Follower Count
    owner_fol = df.groupby('Owner')['Follower'].max().nlargest(10).reset_index()
    fig4 = px.bar(owner_fol, x='Follower', y='Owner', orientation='h', 
                  title="Top 10 Accounts by Follower Count", color='Follower')
    fig4.update_layout(yaxis={'categoryorder':'total ascending'})

    # SIDEBAR
    st.sidebar.header("Export Center")
    if st.sidebar.button("Generate Color PDF Report"):
        with st.spinner("Capturing charts and building PDF..."):
            pdf_data = create_visual_pdf(df, stats, [fig1, fig2, fig3, fig4])
            st.sidebar.download_button(
                label="⬇️ Download Visual PDF",
                data=pdf_data,
                file_name="SM_Detailed_Visual_Report.pdf",
                mime="application/pdf"
            )

    # WEB INTERFACE METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Impressions", f"{stats['imp']:,.0f}")
    m2.metric("Total Engagement", f"{stats['eng']:,.0f}")
    m3.metric("Total Contents", stats['cnt'])

    st.divider()

    # WEB INTERFACE CHARTS
    c1, c2 = st.columns(2)
    c1.plotly_chart(fig1, use_container_width=True)
    c2.plotly_chart(fig2, use_container_width=True)
    
    st.divider()
    
    c3, c4 = st.columns(2)
    c3.plotly_chart(fig3, use_container_width=True)
    c4.plotly_chart(fig4, use_container_width=True)

except Exception as e:
    st.error(f"Application Error: {e}")
