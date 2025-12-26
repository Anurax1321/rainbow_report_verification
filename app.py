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
import pandas as pd
from io import BytesIO
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

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

def generate_html_report(results):
    """Generate professional HTML report with analysis results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Neonatal Screening Analysis Report</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f7fafc;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2em;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
            }}
            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .summary-card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .summary-card h3 {{
                margin: 0 0 10px 0;
                color: #4a5568;
                font-size: 0.9em;
            }}
            .summary-card .value {{
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }}
            .status-box {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .status-success {{
                border-left: 5px solid #28a745;
                background: #d4edda;
            }}
            .status-warning {{
                border-left: 5px solid #ffc107;
                background: #fff3cd;
            }}
            .report-section {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .report-section h2 {{
                margin: 0 0 15px 0;
                color: #2d3748;
                border-bottom: 2px solid #e2e8f0;
                padding-bottom: 10px;
            }}
            .patient-info {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                margin-bottom: 15px;
            }}
            .patient-info div {{
                padding: 8px;
                background: #f7fafc;
                border-radius: 5px;
            }}
            .patient-info strong {{
                color: #4a5568;
            }}
            .abnormality {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
            }}
            .abnormality h4 {{
                margin: 0 0 10px 0;
                color: #856404;
            }}
            .abnormality p {{
                margin: 5px 0;
                color: #856404;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e2e8f0;
            }}
            th {{
                background: #f7fafc;
                font-weight: 600;
                color: #2d3748;
            }}
            .footer {{
                text-align: center;
                color: #718096;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e2e8f0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏥 Vijayrekha Life Sciences™</h1>
            <h2>Neonatal Screening Report Analysis</h2>
            <p>Care that never quits</p>
            <p>Generated: {timestamp}</p>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <h3>Total Reports</h3>
                <div class="value">{results['total']}</div>
            </div>
            <div class="summary-card">
                <h3>Successfully Processed</h3>
                <div class="value">{results['successful']}</div>
            </div>
            <div class="summary-card">
                <h3>Normal Reports</h3>
                <div class="value" style="color: #28a745;">{results['normal']}</div>
            </div>
            <div class="summary-card">
                <h3>Abnormal Reports</h3>
                <div class="value" style="color: #dc3545;">{results['abnormal']}</div>
            </div>
        </div>
    """

    # Overall status
    if results['abnormal'] == 0:
        html_content += """
        <div class="status-box status-success">
            <h2 style="color: #155724; margin: 0;">✅ All Reports Are Clean!</h2>
            <p style="color: #155724; margin: 10px 0 0 0;">No abnormalities detected. All test values are within normal reference ranges.</p>
        </div>
        """
    else:
        html_content += f"""
        <div class="status-box status-warning">
            <h2 style="color: #856404; margin: 0;">⚠️ {results['abnormal']} Report(s) with Abnormalities Found</h2>
            <p style="color: #856404; margin: 10px 0 0 0;">The following reports require attention:</p>
        </div>
        """

        # List abnormal reports
        html_content += '<div class="report-section"><h2>Reports Requiring Attention</h2><table><thead><tr><th>#</th><th>File</th><th>Patient</th><th>Abnormalities</th></tr></thead><tbody>'

        for idx, analyzer in enumerate(results['abnormal_reports'], 1):
            patient_name = analyzer.patient_info.get('name', 'N/A')
            html_content += f'<tr><td>{idx}</td><td>{analyzer.relative_path}</td><td>{patient_name}</td><td>{len(analyzer.abnormalities)}</td></tr>'

        html_content += '</tbody></table></div>'

        # Detailed abnormal reports
        html_content += '<h2 style="margin-top: 30px;">Detailed Reports (Abnormal Cases)</h2>'

        for analyzer in results['abnormal_reports']:
            html_content += f'<div class="report-section"><h2>📄 {analyzer.relative_path}</h2>'

            # Patient information
            html_content += '<div class="patient-info">'
            if 'name' in analyzer.patient_info:
                html_content += f'<div><strong>Name:</strong> {analyzer.patient_info["name"]}</div>'
            if 'uhid' in analyzer.patient_info:
                html_content += f'<div><strong>UHID:</strong> {analyzer.patient_info["uhid"]}</div>'
            if 'age_gender' in analyzer.patient_info:
                html_content += f'<div><strong>Age/Gender:</strong> {analyzer.patient_info["age_gender"]}</div>'
            if 'collected_on' in analyzer.patient_info:
                html_content += f'<div><strong>Collected:</strong> {analyzer.patient_info["collected_on"]}</div>'
            html_content += '</div>'

            # Abnormalities
            categories = {}
            for abn in analyzer.abnormalities:
                cat = abn['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(abn)

            html_content += '<h3 style="margin-top: 20px;">⚠️ Abnormalities Found:</h3>'
            for category, abnorms in categories.items():
                html_content += f'<h4>{category} ({len(abnorms)} issue(s))</h4>'
                for abn in abnorms:
                    unit_str = f" {abn['unit']}" if abn['unit'] else ""
                    html_content += f'''
                    <div class="abnormality">
                        <h4>⚠️ {abn['analyte']}</h4>
                        <p><strong>Value:</strong> {abn['value']}{unit_str}</p>
                        <p><strong>Reference Range:</strong> {abn['reference_range']}{unit_str}</p>
                        <p><strong>Issue:</strong> {abn['reason']}</p>
                    </div>
                    '''

            html_content += '</div>'

    # Footer
    html_content += """
        <div class="footer">
            <p><strong>Vijayrekha Life Sciences™</strong></p>
            <p>📧 info@vijayrekhals.co.in | 🌐 www.vijayrekhals.co.in | ☎️ +91-4035893249</p>
            <p><em>Care that never quits</em></p>
        </div>
    </body>
    </html>
    """

    return html_content.encode('utf-8')

def generate_excel_report(results):
    """Generate Excel file with analysis results."""
    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Summary Statistics
        summary_data = {
            'Metric': ['Total Reports', 'Successfully Processed', 'Failed', 'Normal Reports', 'Abnormal Reports'],
            'Count': [results['total'], results['successful'], results['failed'], results['normal'], results['abnormal']]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # Sheet 2: Abnormal Reports List
        if results['abnormal_reports']:
            abnormal_list = []
            for analyzer in results['abnormal_reports']:
                abnormal_list.append({
                    'File': analyzer.relative_path,
                    'Patient Name': analyzer.patient_info.get('name', 'N/A'),
                    'UHID': analyzer.patient_info.get('uhid', 'N/A'),
                    'Age/Gender': analyzer.patient_info.get('age_gender', 'N/A'),
                    'Collected On': analyzer.patient_info.get('collected_on', 'N/A'),
                    'Reported On': analyzer.patient_info.get('reported_on', 'N/A'),
                    'Total Abnormalities': len(analyzer.abnormalities)
                })
            abnormal_df = pd.DataFrame(abnormal_list)
            abnormal_df.to_excel(writer, sheet_name='Abnormal Reports', index=False)

        # Sheet 3: Detailed Abnormalities
        if results['abnormal_reports']:
            detailed_abnormalities = []
            for analyzer in results['abnormal_reports']:
                for abn in analyzer.abnormalities:
                    detailed_abnormalities.append({
                        'File': analyzer.relative_path,
                        'Patient Name': analyzer.patient_info.get('name', 'N/A'),
                        'Category': abn['category'],
                        'Analyte': abn['analyte'],
                        'Value': abn['value'],
                        'Unit': abn['unit'],
                        'Reference Range': abn['reference_range'],
                        'Issue': abn['reason']
                    })
            abnormalities_df = pd.DataFrame(detailed_abnormalities)
            abnormalities_df.to_excel(writer, sheet_name='Detailed Abnormalities', index=False)

        # Sheet 4: All Reports (Normal + Abnormal)
        all_reports_list = []
        for analyzer in results['abnormal_reports'] + results['normal_reports']:
            all_reports_list.append({
                'File': analyzer.relative_path,
                'Patient Name': analyzer.patient_info.get('name', 'N/A'),
                'UHID': analyzer.patient_info.get('uhid', 'N/A'),
                'Age/Gender': analyzer.patient_info.get('age_gender', 'N/A'),
                'Collected On': analyzer.patient_info.get('collected_on', 'N/A'),
                'Reported On': analyzer.patient_info.get('reported_on', 'N/A'),
                'Status': 'Abnormal' if len(analyzer.abnormalities) > 0 else 'Normal',
                'Abnormality Count': len(analyzer.abnormalities)
            })
        all_reports_df = pd.DataFrame(all_reports_list)
        all_reports_df.to_excel(writer, sheet_name='All Reports', index=False)

    output.seek(0)
    return output

# Logo display
logo_path = Path("assets/logo.png")
if logo_path.exists():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(str(logo_path), use_column_width=True)
else:
    st.warning("⚠️ Logo file not found at assets/logo.png")

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
        # Clean up any existing temp files first
        if 'temp_dir' in st.session_state and Path(st.session_state.temp_dir).exists():
            try:
                shutil.rmtree(st.session_state.temp_dir, ignore_errors=True)
            except:
                pass

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            st.session_state.temp_file_path = tmp_file.name

    # Analyze button
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔄 Reset", use_container_width=True, help="Clear all data and start fresh"):
            # Clean up temp files before clearing session
            if 'temp_file_path' in st.session_state:
                try:
                    temp_file = Path(st.session_state.temp_file_path)
                    if temp_file.exists():
                        temp_file.unlink()
                except:
                    pass

            if 'temp_dir' in st.session_state:
                try:
                    temp_dir = Path(st.session_state.temp_dir)
                    if temp_dir.exists():
                        shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass

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
            try:
                file_path = Path(st.session_state.temp_file_path)

                # Check if ZIP or PDF
                if file_path.suffix.lower() == '.zip':
                    # Extract ZIP with progress
                    with st.status("📦 Extracting ZIP file...", expanded=True) as status:
                        st.write("Extracting files from ZIP archive...")
                        temp_dir, pdf_files = extract_zip_file(file_path)
                        st.write(f"✅ Found {len(pdf_files)} PDF file(s)")
                        status.update(label="✅ Extraction complete!", state="complete")

                    # Process all PDFs with progress bar
                    st.markdown("### 🔄 Processing Reports")
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    results = {
                        'total': len(pdf_files),
                        'successful': 0,
                        'failed': 0,
                        'normal': 0,
                        'abnormal': 0,
                        'abnormal_reports': [],
                        'normal_reports': [],
                        'failed_reports': [],
                        'is_zip': True,
                        'temp_dir': temp_dir
                    }

                    for idx, (pdf_path, rel_path) in enumerate(pdf_files, 1):
                        # Update progress
                        progress = idx / len(pdf_files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing {idx}/{len(pdf_files)}: {rel_path}")

                        try:
                            analyzer = NeonatalReportAnalyzer(str(pdf_path), rel_path)
                            analyzer.extract_text_from_pdf(quiet=True)
                            analyzer.parse_patient_info()
                            analyzer.parse_biochemical_parameters()
                            analyzer.parse_amino_acids()
                            analyzer.parse_amino_acid_ratios()
                            analyzer.parse_acylcarnitines()
                            analyzer.parse_acylcarnitine_ratios()
                            analyzer.validate_all_values()

                            results['successful'] += 1

                            if len(analyzer.abnormalities) > 0:
                                results['abnormal'] += 1
                                results['abnormal_reports'].append(analyzer)
                            else:
                                results['normal'] += 1
                                results['normal_reports'].append(analyzer)

                        except Exception as e:
                            results['failed'] += 1
                            results['failed_reports'].append({
                                'path': rel_path,
                                'error': str(e)
                            })

                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    st.success(f"✅ Processing complete! {results['successful']}/{results['total']} files processed successfully")

                    st.session_state.results = results

                elif file_path.suffix.lower() == '.pdf':
                    # Process single PDF with status
                    with st.status("🔄 Processing PDF...", expanded=True) as status:
                        st.write("Extracting text from PDF...")
                        analyzer = NeonatalReportAnalyzer(str(file_path), file_path.name)
                        analyzer.extract_text_from_pdf(quiet=True)

                        st.write("Parsing patient information...")
                        analyzer.parse_patient_info()

                        st.write("Analyzing biochemical parameters...")
                        analyzer.parse_biochemical_parameters()

                        st.write("Analyzing amino acids...")
                        analyzer.parse_amino_acids()
                        analyzer.parse_amino_acid_ratios()

                        st.write("Analyzing acylcarnitines...")
                        analyzer.parse_acylcarnitines()
                        analyzer.parse_acylcarnitine_ratios()

                        st.write("Validating all values...")
                        analyzer.validate_all_values()

                        status.update(label="✅ Analysis complete!", state="complete")

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

                except FileNotFoundError as e:
                    st.error("❌ **File Not Found**")
                    st.markdown("""
                    <div class="info-box">
                        <strong>The uploaded file could not be found.</strong><br>
                        Please try:
                        <ul>
                            <li>Re-uploading the file</li>
                            <li>Clicking the Reset button and starting over</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.results = None

                except zipfile.BadZipFile as e:
                    st.error("❌ **Invalid ZIP File**")
                    st.markdown("""
                    <div class="info-box">
                        <strong>The ZIP file appears to be corrupted or invalid.</strong><br>
                        Please ensure:
                        <ul>
                            <li>The file is a valid ZIP archive</li>
                            <li>The file was completely uploaded</li>
                            <li>The file is not password-protected</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.results = None

                except PermissionError as e:
                    st.error("❌ **Permission Denied**")
                    st.markdown("""
                    <div class="info-box">
                        <strong>Cannot access the file due to permission restrictions.</strong><br>
                        Please:
                        <ul>
                            <li>Check file permissions</li>
                            <li>Make sure the file is not open in another program</li>
                            <li>Try uploading again</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.results = None

                except Exception as e:
                    error_msg = str(e).lower()
                    st.error("❌ **Processing Error**")

                    # Provide context-specific error messages
                    if "pdf" in error_msg or "pdfplumber" in error_msg:
                        st.markdown("""
                        <div class="info-box">
                            <strong>Problem reading PDF file.</strong><br>
                            Possible causes:
                            <ul>
                                <li>PDF file may be corrupted</li>
                                <li>PDF may be password-protected</li>
                                <li>PDF format may not be supported</li>
                            </ul>
                            <strong>Suggestion:</strong> Try opening the PDF in a reader to verify it's valid.
                        </div>
                        """, unsafe_allow_html=True)
                    elif "text" in error_msg or "extract" in error_msg:
                        st.markdown("""
                        <div class="info-box">
                            <strong>Problem extracting text from PDF.</strong><br>
                            This usually means:
                            <ul>
                                <li>The PDF contains only images (scanned document)</li>
                                <li>The PDF uses an unsupported format</li>
                            </ul>
                            <strong>Suggestion:</strong> Ensure your PDF contains actual text, not scanned images.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="info-box">
                            <strong>An unexpected error occurred:</strong><br>
                            <code>{str(e)}</code><br><br>
                            <strong>What you can do:</strong>
                            <ul>
                                <li>Click the Reset button and try again</li>
                                <li>Verify your file is a valid neonatal screening report</li>
                                <li>Try with a different file to see if the issue persists</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)

                    # Show detailed error in expander for debugging
                    with st.expander("🔍 Technical Details (for debugging)"):
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

            # Batch Statistics Dashboard (for multiple files)
            if results['total'] > 1:
                st.markdown("### 📈 Batch Statistics Dashboard")

                # Calculate statistics
                total_abnormalities = sum(len(analyzer.abnormalities) for analyzer in results['abnormal_reports'])
                avg_abnormalities = total_abnormalities / results['total'] if results['total'] > 0 else 0
                success_rate = (results['successful'] / results['total'] * 100) if results['total'] > 0 else 0

                # Get most common abnormality categories
                category_counts = {}
                for analyzer in results['abnormal_reports']:
                    for abn in analyzer.abnormalities:
                        cat = abn['category']
                        category_counts[cat] = category_counts.get(cat, 0) + 1

                most_common_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else "None"

                # Display dashboard metrics
                dash_col1, dash_col2, dash_col3, dash_col4 = st.columns(4)

                with dash_col1:
                    st.metric(
                        "Success Rate",
                        f"{success_rate:.1f}%",
                        delta=f"{results['successful']} successful" if results['failed'] == 0 else f"-{results['failed']} failed",
                        delta_color="normal" if results['failed'] == 0 else "inverse"
                    )

                with dash_col2:
                    st.metric(
                        "Total Abnormalities",
                        total_abnormalities,
                        delta=f"Across {results['abnormal']} reports" if results['abnormal'] > 0 else "All clean!"
                    )

                with dash_col3:
                    st.metric(
                        "Avg Abnormalities/Report",
                        f"{avg_abnormalities:.2f}",
                        delta=f"{results['abnormal']} affected" if results['abnormal'] > 0 else "0 affected",
                        delta_color="inverse" if results['abnormal'] > 0 else "normal"
                    )

                with dash_col4:
                    st.metric(
                        "Most Common Issue",
                        most_common_category[:15] + "..." if len(most_common_category) > 15 else most_common_category,
                        delta=f"{category_counts.get(most_common_category, 0)} cases" if most_common_category != "None" else "No issues"
                    )

                # Additional insights
                if results['abnormal_reports']:
                    st.markdown("#### 📊 Key Insights")

                    insight_col1, insight_col2 = st.columns(2)

                    with insight_col1:
                        # Reports with highest abnormalities
                        top_abnormal = sorted(results['abnormal_reports'], key=lambda x: len(x.abnormalities), reverse=True)[:3]
                        st.markdown("**⚠️ Reports with Most Issues:**")
                        for idx, analyzer in enumerate(top_abnormal, 1):
                            st.markdown(f"{idx}. {analyzer.relative_path.split('/')[-1][:40]}... ({len(analyzer.abnormalities)} issues)")

                    with insight_col2:
                        # Most frequent abnormal analytes
                        analyte_counts = {}
                        for analyzer in results['abnormal_reports']:
                            for abn in analyzer.abnormalities:
                                analyte = abn['analyte']
                                analyte_counts[analyte] = analyte_counts.get(analyte, 0) + 1

                        if analyte_counts:
                            top_analytes = sorted(analyte_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                            st.markdown("**🔬 Most Frequent Abnormal Tests:**")
                            for analyte, count in top_analytes:
                                st.markdown(f"• {analyte}: {count} case(s)")

                st.markdown("---")

            # Visual Analytics
            if results['total'] > 1:  # Only show charts if multiple files
                st.markdown("### 📊 Visual Analytics")

                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:
                    # Pie chart: Normal vs Abnormal
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=['Normal', 'Abnormal'],
                        values=[results['normal'], results['abnormal']],
                        marker=dict(colors=['#28a745', '#dc3545']),
                        hole=0.4
                    )])
                    fig_pie.update_layout(
                        title="Report Status Distribution",
                        height=400,
                        showlegend=True
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                with chart_col2:
                    # Bar chart: Abnormality counts by category
                    if results['abnormal_reports']:
                        category_counts = {}
                        for analyzer in results['abnormal_reports']:
                            for abn in analyzer.abnormalities:
                                cat = abn['category']
                                category_counts[cat] = category_counts.get(cat, 0) + 1

                        if category_counts:
                            fig_bar = go.Figure(data=[go.Bar(
                                x=list(category_counts.keys()),
                                y=list(category_counts.values()),
                                marker_color='#ffc107'
                            )])
                            fig_bar.update_layout(
                                title="Abnormalities by Category",
                                xaxis_title="Category",
                                yaxis_title="Count",
                                height=400
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)
                        else:
                            st.info("No abnormalities to display")
                    else:
                        st.success("✅ No abnormalities detected!")

                # Additional chart: Abnormalities per report
                if results['abnormal_reports']:
                    st.markdown("#### Abnormalities Distribution Across Reports")

                    report_data = []
                    for analyzer in results['abnormal_reports']:
                        report_data.append({
                            'Report': analyzer.relative_path.split('/')[-1][:30] + '...' if len(analyzer.relative_path) > 30 else analyzer.relative_path,
                            'Abnormalities': len(analyzer.abnormalities)
                        })

                    df_reports = pd.DataFrame(report_data)
                    fig_hist = px.bar(
                        df_reports,
                        x='Report',
                        y='Abnormalities',
                        color='Abnormalities',
                        color_continuous_scale='Reds'
                    )
                    fig_hist.update_layout(
                        xaxis_title="Report",
                        yaxis_title="Number of Abnormalities",
                        height=400,
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)

                st.markdown("---")

            # Download Options
            st.markdown("### 📥 Download Reports")
            download_col1, download_col2, download_col3 = st.columns(3)

            with download_col1:
                # Excel Export
                excel_file = generate_excel_report(results)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="📊 Download Excel Report",
                    data=excel_file,
                    file_name=f"neonatal_analysis_{timestamp}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help="Download detailed analysis as Excel spreadsheet with multiple sheets"
                )

            with download_col2:
                # HTML Export
                html_file = generate_html_report(results)
                st.download_button(
                    label="📄 Download HTML Report",
                    data=html_file,
                    file_name=f"neonatal_analysis_{timestamp}.html",
                    mime="text/html",
                    use_container_width=True,
                    help="Download detailed analysis as a self-contained HTML file"
                )

            with download_col3:
                st.markdown("""
                <div style="background-color: #e6f3ff; padding: 0.75rem; border-radius: 5px; text-align: center;">
                    <strong>💡 Tip:</strong> Download HTML and print to PDF
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Toggle to show all reports
            show_all_reports = st.checkbox(
                "📄 Show all reports (including normal ones)",
                value=False,
                help="Check this to view detailed reports for all processed files, not just abnormal ones"
            )

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

            # Search and Filter
            if results['total'] > 1:
                st.markdown("### 🔍 Search & Filter Reports")

                filter_col1, filter_col2, filter_col3 = st.columns(3)

                with filter_col1:
                    search_term = st.text_input("🔎 Search by patient name or file", "", help="Enter patient name or filename to filter")

                with filter_col2:
                    status_filter = st.selectbox("📊 Filter by status", ["All", "Normal Only", "Abnormal Only"])

                with filter_col3:
                    if results['abnormal_reports']:
                        # Get all unique categories
                        all_categories = set()
                        for analyzer in results['abnormal_reports']:
                            for abn in analyzer.abnormalities:
                                all_categories.add(abn['category'])
                        category_filter = st.selectbox("🏷️ Filter by abnormality type", ["All"] + sorted(list(all_categories)))
                    else:
                        category_filter = "All"

                st.markdown("---")

            # Detailed reports section
            reports_to_show = []
            section_title = "### 📋 Detailed Reports"

            if show_all_reports:
                # Show all reports (both abnormal and normal)
                reports_to_show = results['abnormal_reports'] + results['normal_reports']
                section_title = f"### 📋 Detailed Reports - All {len(reports_to_show)} Report(s)"
            elif results['abnormal'] > 0:
                # Show only abnormal reports
                reports_to_show = results['abnormal_reports']
                section_title = "### 📋 Detailed Reports (Abnormal Cases Only)"

            # Apply filters
            if results['total'] > 1:
                filtered_reports = []

                for analyzer in reports_to_show:
                    # Search filter
                    if search_term:
                        search_lower = search_term.lower()
                        patient_name = analyzer.patient_info.get('name', '').lower()
                        file_path = analyzer.relative_path.lower()

                        if search_lower not in patient_name and search_lower not in file_path:
                            continue

                    # Status filter
                    if status_filter == "Normal Only" and len(analyzer.abnormalities) > 0:
                        continue
                    if status_filter == "Abnormal Only" and len(analyzer.abnormalities) == 0:
                        continue

                    # Category filter
                    if category_filter != "All":
                        has_category = False
                        for abn in analyzer.abnormalities:
                            if abn['category'] == category_filter:
                                has_category = True
                                break
                        if not has_category:
                            continue

                    filtered_reports.append(analyzer)

                reports_to_show = filtered_reports
                if search_term or status_filter != "All" or category_filter != "All":
                    section_title = f"### 📋 Filtered Results - {len(reports_to_show)} Report(s)"

            if reports_to_show:
                st.markdown(section_title)

                for analyzer in reports_to_show:
                    # Create expander title based on abnormalities
                    if len(analyzer.abnormalities) > 0:
                        expander_title = f"⚠️ {analyzer.relative_path} - {len(analyzer.abnormalities)} abnormality(ies)"
                        is_expanded = True
                    else:
                        expander_title = f"✅ {analyzer.relative_path} - Normal"
                        is_expanded = False

                    with st.expander(expander_title, expanded=is_expanded):

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
                        if len(analyzer.abnormalities) > 0:
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
                        else:
                            st.success("✅ All values are within normal range")

            # Report Comparison Tool
            if results['total'] > 1:
                st.markdown("---")
                st.markdown("### 🔄 Compare Reports Side-by-Side")

                all_analyzers = results['abnormal_reports'] + results['normal_reports']
                report_names = [f"{analyzer.relative_path} ({'⚠️ Abnormal' if len(analyzer.abnormalities) > 0 else '✅ Normal'})"
                               for analyzer in all_analyzers]

                if len(all_analyzers) >= 2:
                    st.markdown("Select 2-3 reports to compare:")

                    comparison_col1, comparison_col2, comparison_col3 = st.columns(3)

                    with comparison_col1:
                        report1_idx = st.selectbox("Report 1", range(len(report_names)), format_func=lambda x: report_names[x], key="compare_1")

                    with comparison_col2:
                        available_for_2 = [i for i in range(len(report_names)) if i != report1_idx]
                        report2_idx = st.selectbox("Report 2", available_for_2, format_func=lambda x: report_names[x], key="compare_2")

                    with comparison_col3:
                        available_for_3 = [i for i in range(len(report_names)) if i not in [report1_idx, report2_idx]]
                        if available_for_3:
                            report3_idx = st.selectbox("Report 3 (Optional)", [None] + available_for_3,
                                                      format_func=lambda x: "None" if x is None else report_names[x], key="compare_3")
                        else:
                            report3_idx = None

                    if st.button("📊 Compare Selected Reports", use_container_width=True):
                        st.markdown("#### Comparison Results")

                        selected_analyzers = [all_analyzers[report1_idx], all_analyzers[report2_idx]]
                        if report3_idx is not None:
                            selected_analyzers.append(all_analyzers[report3_idx])

                        # Create comparison table
                        cols = st.columns(len(selected_analyzers))

                        for idx, analyzer in enumerate(selected_analyzers):
                            with cols[idx]:
                                st.markdown(f"**{analyzer.relative_path}**")

                                # Patient info
                                st.markdown("---")
                                if 'name' in analyzer.patient_info:
                                    st.write(f"👤 {analyzer.patient_info['name']}")
                                if 'age_gender' in analyzer.patient_info:
                                    st.write(f"📋 {analyzer.patient_info['age_gender']}")

                                # Status
                                st.markdown("---")
                                total_tests = (len(analyzer.amino_acids) + len(analyzer.amino_acid_ratios) +
                                             len(analyzer.acylcarnitines) + len(analyzer.acylcarnitine_ratios))
                                st.metric("Total Tests", total_tests)
                                st.metric("Abnormalities", len(analyzer.abnormalities),
                                         delta=f"-{total_tests - len(analyzer.abnormalities)}" if len(analyzer.abnormalities) == 0 else None,
                                         delta_color="inverse")

                                # Abnormalities list
                                if len(analyzer.abnormalities) > 0:
                                    st.markdown("**Issues:**")
                                    for abn in analyzer.abnormalities[:5]:  # Show first 5
                                        st.markdown(f"• {abn['analyte']}")
                                    if len(analyzer.abnormalities) > 5:
                                        st.markdown(f"*...and {len(analyzer.abnormalities) - 5} more*")
                                else:
                                    st.success("✅ All Normal")
                else:
                    st.info("Need at least 2 reports for comparison")

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
