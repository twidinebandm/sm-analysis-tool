import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io

# 1. CONFIGURATION - Güncel GitHub Raw URL
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
    pdf.add_page()
    
    # Executive Summary Metrics
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Executive Summary Metrics", ln=True)
    pdf.set_font("Helvetica", "", 11)
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
    
    pdf.add_page()
    # Chart 3: Top 10 Content Owners by Impressions
    pdf.cell(0, 10, "3. Top 10 Content Owners by Impressions", ln=True)
    img_bytes3 = figs[2].to_image(format="png", width=800, height=450)
    pdf.image(io.BytesIO(img_bytes3), x=10, y=None, w=180)
    pdf.ln(
