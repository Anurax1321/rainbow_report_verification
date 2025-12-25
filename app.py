"""
Neonatal Screening Report Analyzer - Streamlit Web Application
Vijayrekha Life Sciences
"""

import streamlit as st
import tempfile
from pathlib import Path
import sys

# Page configuration
st.set_page_config(
    page_title="Neonatal Report Analyzer - Vijayrekha Life Sciences",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .company-name {
        font-size: 2rem;
        font-weight: bold;
        color: #4a5568;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .tagline {
        font-size: 1.2rem;
        color: #68b984;
        text-align: center;
        font-style: italic;
        margin-bottom: 2rem;
    }
    .upload-section {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f7fafc;
    }
    .info-box {
        background-color: #e6f3ff;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header with logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Try to display logo
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        st.image(str(logo_path), width=300)

    st.markdown('<div class="company-name">Vijayrekha Life Sciences™</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Care that never quits</div>', unsafe_allow_html=True)

# Main title
st.markdown("""
<div class="main-header">
    <h1>🏥 Neonatal Screening Report Analyzer</h1>
    <p>Automated validation of neonatal metabolic screening reports</p>
</div>
""", unsafe_allow_html=True)

# Instructions
st.markdown("""
<div class="info-box">
    <h3>📋 How to Use:</h3>
    <ol>
        <li><strong>Upload your file</strong> - Single PDF or ZIP file containing multiple reports</li>
        <li><strong>Click "Analyze Reports"</strong> - The system will process and validate all test values</li>
        <li><strong>Review results</strong> - See summary statistics and detailed abnormalities</li>
        <li><strong>Download reports</strong> - Get professional HTML or Excel reports</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# File upload section
st.markdown("## 📁 Upload Files")

uploaded_file = st.file_uploader(
    "Drop your PDF or ZIP file here",
    type=["pdf", "zip"],
    help="Upload a single PDF report or a ZIP file containing multiple PDF reports"
)

# Display file information if uploaded
if uploaded_file is not None:
    file_details = {
        "Filename": uploaded_file.name,
        "File Size": f"{uploaded_file.size / 1024:.2f} KB",
        "File Type": uploaded_file.type
    }

    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.success("✅ File uploaded successfully!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Filename", uploaded_file.name)
    col2.metric("Size", f"{uploaded_file.size / (1024*1024):.2f} MB")
    col3.metric("Type", "ZIP" if uploaded_file.name.endswith('.zip') else "PDF")

    st.markdown('</div>', unsafe_allow_html=True)

    # Save uploaded file temporarily
    if 'temp_file_path' not in st.session_state:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            st.session_state.temp_file_path = tmp_file.name

    # Analyze button
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("🚀 Analyze Reports", type="primary", use_container_width=True)

    if analyze_button:
        st.session_state.analyze_clicked = True
        st.rerun()

    # Show processing section if analyze was clicked
    if st.session_state.get('analyze_clicked', False):
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")

        # This will be filled in Phase 2
        with st.spinner("Processing reports..."):
            st.info("🔄 Processing functionality will be added in Phase 2")
            st.info(f"File ready for processing: {st.session_state.temp_file_path}")

else:
    st.info("👆 Please upload a PDF or ZIP file to begin analysis")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p><strong>Vijayrekha Life Sciences™</strong></p>
    <p>📧 info@vijayrekhals.co.in | 🌐 www.vijayrekhals.co.in | ☎️ +91-4035893249</p>
    <p><em>Care that never quits</em></p>
</div>
""", unsafe_allow_html=True)
