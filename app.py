import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io

# 1. GITHUB RAW URL CONFIGURATION
GITHUB_CSV_URL = "https://raw.githubusercontent.com/twidinebandm/sm-analysis-tool/refs/heads/main/yaya.csv"
GITHUB_LOGO_URL = "https://raw.githubusercontent.com/twidinebandm/sm-analysis-tool/refs/heads/main/CONCEPT_LOGO%20(1)_beyaz.png"

# Page Configuration
st.set_page_config(page_title="Concept Istanbul Social Media Analytics Tool", layout="wide")

# --- UNICODE SAFE PDF CLASS ---
class SafePDF(FPDF):
    def header(self):
        try:
            if hasattr(self, 'logo_bytes'):
                self.image(self.logo_bytes, x=10, y=10, w=40) # Sola dayalı logo
                self.ln(20)
        except:
            pass

        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Social Media Performance Visual Report", ln=True, align="L")
        self.ln(5)

    def safe_text(self, text):
        return str(text).encode('latin-1', 'replace').decode('latin-1')

def create_visual_pdf(df, stats, figs, logo_bytes):
    pdf = SafePDF()
    pdf.logo_bytes = io.BytesIO(logo_bytes) if logo_bytes else None
    
    pdf.add_page()
    
    # Header Section
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Executive Summary Metrics", ln=True)
    pdf.set_font("Helvetica", "", 11)
    
    pdf.cell(60, 10, f"Total Impressions: {stats['imp']:,.0f}", border=1)
    pdf.cell(60, 10, f"Total Engagement: {stats['eng']:,.0f}", border=1)
    pdf.cell(60, 10, f"Total Contents: {stats['cnt']}", border=1)
    pdf.ln(15)

    # Charts
    titles = [
        "1. Impression Share by Platform",
        "2. Top 10 Owners by Engagement",
        "3. Top 10 Content Owners by Impressions",
        "4. Top 10 Accounts by Follower Count"
    ]
    
    for i, fig in enumerate(figs):
        if i == 2: pdf.add_page() # 3. grafikten önce yeni sayfa
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, titles[i], ln=True)
        img_bytes = fig.to_image(format="png", width=800, height=450)
        pdf.image(io.BytesIO(img_bytes), x=10, y=None, w=180)
        pdf.ln(5)
    
    return bytes(pdf.output())

# --- DATA PROCESSING ---
def process_data(df):
    df.columns = [c.strip() for c in df.columns]
    df['Follower'] = pd.to_numeric(df['Follower'], errors='coerce').fillna(0)
    df['Engagement'] = pd.to_numeric(df['Engagement'], errors='coerce').fillna(0)
    df['Calculated_Impression'] = pd.to_numeric(df.get('Average Impression', 0), errors='coerce').fillna(0)
    if 'Name' in df.columns:
        df['Owner'] = df['Name'].fillna(df['Medium'])
    else:
        df['Owner'] = df['Medium']
    return df

# --- MAIN APP LAYOUT (SOLA DAYALI LOGO VE BAŞLIK) ---
# Logo ve Başlığı aynı satırda sola dayalı hizalamak için sütunları ayarlıyoruz
col_logo, col_title = st.columns([1, 6]) 

with col_logo:
    try:
        st.image(GITHUB_LOGO_URL, width=120)
    except:
        pass

with col_title:
    # Başlığı logonun yanına, dikeyde ortalanmış hissi verecek şekilde biraz boşlukla ekliyoruz
    st.markdown("<h1 style='margin-top: -10px;'>Concept Istanbul Social Media Analytics Tool</h1>", unsafe_allow_html=True)

try:
    df_raw = pd.read_csv(GITHUB_CSV_URL)
    df = process_data(df_raw)
    
    stats = {
        'imp': df['Calculated_Impression'].sum(),
        'eng': df['Engagement'].sum(),
        'cnt': len(df)
    }

    # Grafikler (İsimler ve renkler korundu)
    fig1 = px.pie(df, values='Calculated_Impression', names='Medium', hole=0.4, 
                  title="Impression Share by Platform", color_discrete_sequence=px.colors.qualitative.Bold)
    
    owner_eng = df.groupby('Owner')['Engagement'].sum().nlargest(10).reset_index()
    fig2 = px.bar(owner_eng, x='Engagement', y='Owner', orientation='h', 
                  title="Top 10 Owners by Engagement", color='Owner', color_discrete_sequence=px.colors.qualitative.Pastel)
    fig2.update_layout(yaxis={'categoryorder':'total ascending'})
    
    owner_imp = df.groupby('Owner')['Calculated_Impression'].sum().nlargest(10).reset_index()
    fig3 = px.bar(owner_imp, x='Calculated_Impression', y='Owner', orientation='h', 
                  title="Top 10 Content Owners by Impressions", color='Owner', color_discrete_sequence=px.colors.sequential.Viridis)
    fig3.update_layout(yaxis={'categoryorder':'total ascending'})
    
    owner_fol = df.groupby('Owner')['Follower'].max().nlargest(10).reset_index()
    fig4 = px.bar(owner_fol, x='Follower', y='Owner', orientation='h', 
                  title="Top 10 Accounts by Follower Count", color='Follower')
    fig4.update_layout(yaxis={'categoryorder':'total ascending'})

    # SIDEBAR
    st.sidebar.header("Export Options")
    if st.sidebar.button("Generate Color PDF Report"):
        with st.spinner("Generating PDF..."):
            import requests
            try:
                logo_res = requests.get(GITHUB_LOGO_URL)
                logo_b = logo_res.content
            except:
                logo_b = None
            pdf_b = create_visual_pdf(df, stats, [fig1, fig2, fig3, fig4], logo_b)
            st.sidebar.download_button(label="⬇️ Download Visual PDF", data=pdf_b, file_name="Concept_Social_Media_Report.pdf", mime="application/pdf")

    # WEB DISPLAY
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Impressions", f"{stats['imp']:,.0f}")
    m2.metric("Total Engagement", f"{stats['eng']:,.0f}")
    m3.metric("Contents", stats['cnt'])

    st.divider()
    c1, c2 = st.columns(2)
    c1.plotly_chart(fig1, use_container_width=True)
    c2.plotly_chart(fig2, use_container_width=True)
    
    st.divider()
    c3, c4 = st.columns(2)
    c3.plotly_chart(fig3, use_container_width=True)
    c4.plotly_chart(fig4, use_container_width=True)
    
    st.divider()
    st.subheader("📋 Detailed Content Data Table")
    st.dataframe(df.drop(columns=['Calculated_Impression', 'Owner'], errors='ignore'), use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
