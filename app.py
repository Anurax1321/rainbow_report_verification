"""
Neonatal Screening Report Analyzer - Streamlit Web Application
Vijayrekha Life Sciences
"""

import streamlit as st
import tempfile
from pathlib import Path
import sys
import zipfile
import shutil

# Import backend analyzer functions
from report_analyzer import (
    NeonatalReportAnalyzer,
    extract_zip_file,
    process_batch_pdfs
)

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

# TODO: Logo display - working on extracting proper logo from PDF
# logo_path = Path("assets/logo.png")
# if logo_path.exists():
#     st.image(str(logo_path), width=300, use_column_width=False)

# Main title with company branding
st.markdown("""
<div class="main-header">
    <h1>🏥 Vijayrekha Life Sciences™</h1>
    <h2>Neonatal Screening Report Analyzer</h2>
    <p>Care that never quits | Automated validation of neonatal metabolic screening reports</p>
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
    with col1:
        if st.button("🔄 Reset", use_container_width=True, help="Clear all data and start fresh"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    with col2:
        analyze_button = st.button("🚀 Analyze Reports", type="primary", use_container_width=True)

    if analyze_button:
        st.session_state.analyze_clicked = True
        st.rerun()

    # Show processing section if analyze was clicked
    if st.session_state.get('analyze_clicked', False):
        st.markdown("---")
        st.markdown("## 📊 Analysis Results")

        # Process the uploaded file
        if 'results' not in st.session_state:
            with st.spinner("🔄 Processing reports... Please wait..."):
                try:
                    file_path = Path(st.session_state.temp_file_path)

                    # Check if ZIP or PDF
                    if file_path.suffix.lower() == '.zip':
                        # Extract ZIP and process batch
                        temp_dir, pdf_files = extract_zip_file(file_path)

                        # Process all PDFs
                        results = process_batch_pdfs(pdf_files, show_all=False)
                        results['is_zip'] = True
                        results['temp_dir'] = temp_dir

                        st.session_state.results = results

                    elif file_path.suffix.lower() == '.pdf':
                        # Process single PDF
                        analyzer = NeonatalReportAnalyzer(str(file_path), file_path.name)
                        analyzer.extract_text_from_pdf(quiet=True)
                        analyzer.parse_patient_info()
                        analyzer.parse_biochemical_parameters()
                        analyzer.parse_amino_acids()
                        analyzer.parse_amino_acid_ratios()
                        analyzer.parse_acylcarnitines()
                        analyzer.parse_acylcarnitine_ratios()
                        analyzer.validate_all_values()

                        # Store single file results
                        results = {
                            'is_zip': False,
                            'analyzer': analyzer,
                            'total': 1,
                            'successful': 1,
                            'failed': 0,
                            'normal': 1 if len(analyzer.abnormalities) == 0 else 0,
                            'abnormal': 1 if len(analyzer.abnormalities) > 0 else 0,
                            'abnormal_reports': [analyzer] if len(analyzer.abnormalities) > 0 else [],
                            'normal_reports': [analyzer] if len(analyzer.abnormalities) == 0 else []
                        }

                        st.session_state.results = results

                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
                    st.exception(e)
                    st.session_state.results = None

        # Display results if available
        if st.session_state.get('results'):
            results = st.session_state.results

            # Summary Statistics
            st.markdown("### 📈 Summary Statistics")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Reports", results['total'])
            with col2:
                st.metric("Successfully Processed", results['successful'], delta_color="off")
            with col3:
                st.metric("Normal Reports", results['normal'], delta=f"{results['normal']}", delta_color="normal")
            with col4:
                st.metric("Abnormal Reports", results['abnormal'], delta=f"{results['abnormal']}" if results['abnormal'] > 0 else "0", delta_color="inverse")

            st.markdown("---")

            # Overall Status
            if results['abnormal'] == 0:
                st.success("### ✅ ALL REPORTS ARE CLEAN!")
                st.balloons()
                st.markdown("""
                <div style="text-align: center; padding: 2rem; background-color: #d4edda; border-radius: 10px; margin: 1rem 0;">
                    <h2 style="color: #155724;">🎉 No Abnormalities Detected 🎉</h2>
                    <p style="color: #155724; font-size: 1.2rem;">All test values are within normal reference ranges.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"### ⚠️ {results['abnormal']} Report(s) with Abnormalities Found")

                # List abnormal reports
                st.markdown("#### Reports Requiring Attention:")
                for idx, analyzer in enumerate(results['abnormal_reports'], 1):
                    st.markdown(f"**{idx}. {analyzer.relative_path}** - {len(analyzer.abnormalities)} abnormality(ies)")

                st.markdown("---")

                # Detailed reports for abnormal cases
                st.markdown("### 📋 Detailed Reports (Abnormal Cases Only)")

                for analyzer in results['abnormal_reports']:
                    with st.expander(f"🔍 {analyzer.relative_path} - {len(analyzer.abnormalities)} abnormalities", expanded=True):

                        # Patient Information
                        st.markdown("**Patient Information:**")
                        patient_col1, patient_col2 = st.columns(2)

                        with patient_col1:
                            if 'name' in analyzer.patient_info:
                                st.write(f"**Name:** {analyzer.patient_info['name']}")
                            if 'age_gender' in analyzer.patient_info:
                                st.write(f"**Age/Gender:** {analyzer.patient_info['age_gender']}")
                            if 'uhid' in analyzer.patient_info:
                                st.write(f"**UHID:** {analyzer.patient_info['uhid']}")

                        with patient_col2:
                            if 'collected_on' in analyzer.patient_info:
                                st.write(f"**Collected:** {analyzer.patient_info['collected_on']}")
                            if 'reported_on' in analyzer.patient_info:
                                st.write(f"**Reported:** {analyzer.patient_info['reported_on']}")

                        st.markdown("---")

                        # Validation Summary
                        total_tests = (len(analyzer.amino_acids) + len(analyzer.amino_acid_ratios) +
                                      len(analyzer.acylcarnitines) + len(analyzer.acylcarnitine_ratios))

                        sum_col1, sum_col2, sum_col3 = st.columns(3)
                        with sum_col1:
                            st.metric("Total Tests", total_tests)
                        with sum_col2:
                            st.metric("Normal", total_tests - len(analyzer.abnormalities))
                        with sum_col3:
                            st.metric("Abnormal", len(analyzer.abnormalities))

                        st.markdown("---")

                        # Abnormalities Details
                        st.markdown("**⚠️ Abnormalities Found:**")

                        # Group by category
                        categories = {}
                        for abn in analyzer.abnormalities:
                            cat = abn['category']
                            if cat not in categories:
                                categories[cat] = []
                            categories[cat].append(abn)

                        # Display by category
                        for category, abnorms in categories.items():
                            st.markdown(f"**{category}** ({len(abnorms)} issue(s)):")

                            for abn in abnorms:
                                unit_str = f" {abn['unit']}" if abn['unit'] else ""

                                # Create a colored box for each abnormality
                                st.markdown(f"""
                                <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; margin: 0.5rem 0; border-radius: 5px;">
                                    <strong style="color: #856404;">⚠️ {abn['analyte']}</strong><br>
                                    <span style="color: #856404;">Value: <strong>{abn['value']}{unit_str}</strong></span><br>
                                    <span style="color: #856404;">Reference Range: {abn['reference_range']}{unit_str}</span><br>
                                    <span style="color: #721c24;">Issue: {abn['reason']}</span>
                                </div>
                                """, unsafe_allow_html=True)

            # Cleanup temp directory if it was a ZIP
            if results.get('temp_dir') and Path(results['temp_dir']).exists():
                try:
                    shutil.rmtree(results['temp_dir'], ignore_errors=True)
                except:
                    pass

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
