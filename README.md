# Neonatal Screening Report Analyzer

A Python tool to analyze neonatal screening reports (PDF format), extract test values, validate them against reference ranges, and flag abnormalities.

## Features

- **PDF Reading**: Extracts text from multi-page neonatal screening PDFs
- **Patient Information Extraction**: Captures name, age, UHID, dates, etc.
- **Comprehensive Data Parsing**:
  - Biochemical Parameters (TSH, 17-OHP, G-6PD, TGAL, BIOTINDASE, PHENYLALANINE, IRT)
  - Amino Acids (13 analytes)
  - Amino Acid Molar Ratios (5 ratios)
  - Acylcarnitines (33+ analytes)
  - Acylcarnitine Molar Ratios (10 ratios)
- **Smart Reference Range Validation**:
  - Handles multiple range formats: `<3.00`, `0.9-45`, `0-1256`, `0.00 - 0.5`, etc.
  - Automatically flags values outside normal ranges
- **Clear Reporting**:
  - Visual indicators (✓ for normal, ⚠️ for abnormal)
  - Detailed abnormalities report with specific issues
  - Summary statistics

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Single PDF File

```bash
python3 report_analyzer.py
# Then enter the path when prompted:
> ../report/HYDERABAD/BABY OF AMMARA JAMEEL.pdf
```

### Entire Directory

```bash
python3 report_analyzer.py
# Then enter the directory path:
> ../report/HYDERABAD
```

### ZIP File (Multiple Folders)

```bash
python3 report_analyzer.py
# Then enter the ZIP file path:
> ../report/test_reports.zip
```

**ZIP Features:**
- Automatically extracts and processes all PDFs recursively
- Handles duplicate filenames across different folders
- Shows folder structure in output (e.g., `HYDERABAD/BABY OF X.pdf`)
- **Only displays detailed reports for PDFs with abnormalities**
- Cleans up temporary files automatically

## Output

The analyzer produces:

1. **Patient Information**: Demographics and test dates
2. **Biochemical Parameters**: NORMAL/ABNORMAL status for each parameter
3. **Detailed Test Results**: All analytes with values, reference ranges, and validation status
4. **Validation Summary**: Total tests, normal/abnormal counts
5. **Abnormalities Report**: Detailed breakdown of any issues found

### Example Output - Single PDF

```
DETAILED REPORT: BABY OF AMMARA JAMEEL.pdf
================================================================================
Total Tests: 61
Normal: 61
Abnormal: 0

✓ No abnormalities detected. All values are within normal range.
```

### Example Output - ZIP File (All Clean)

```
BATCH ANALYSIS SUMMARY
================================================================================
Source: test_reports.zip
Total PDFs Found: 10
Successfully Processed: 10
Failed: 0

Reports with Abnormalities: 0
Reports Normal: 10
================================================================================

🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉
✓ ALL REPORTS ARE CLEAN! NO ABNORMALITIES DETECTED!
🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉 🎉
```

### Example Output - ZIP File (With Abnormalities)

```
BATCH ANALYSIS SUMMARY
================================================================================
Source: reports.zip
Total PDFs Found: 44
Successfully Processed: 44
Failed: 0

Reports with Abnormalities: 3
Reports Normal: 41
================================================================================

REPORTS WITH ABNORMALITIES:
--------------------------------------------------------------------------------
  1. HYDERABAD/BABY OF X.pdf - 2 abnormality(ies)
  2. PAN INDIA/BABY OF Y.pdf - 1 abnormality(ies)
  3. HYDERABAD/BABY OF Z.pdf - 5 abnormality(ies)
================================================================================

DETAILED REPORTS FOR ABNORMAL CASES
================================================================================

DETAILED REPORT: HYDERABAD/BABY OF X.pdf
================================================================================

PATIENT INFORMATION:
NAME: BABY OF X
AGE GENDER: 0Y 0M 5D / MALE
...

VALIDATION SUMMARY:
Total Tests: 61
Normal: 59
Abnormal: 2

⚠️  ABNORMALITIES REPORT - 2 ISSUE(S) FOUND
================================================================================

Acylcarnitine Abnormalities (2):
  ⚠️  C4OH/C3DC
      Value: 0.75 uM
      Reference Range: 0.00 - 0.5 uM
      Issue: Above maximum (0.5)
  ...
```

## Supported Reference Range Formats

- `<3.00` - Less than (upper limit only)
- `>5.0` - Greater than (lower limit only)
- `0.9-45` - Range (min-max)
- `72.5-816` - Range with decimals
- `0.00 - 0.5` - Range with spaces
- `0.00 -0.429` - Range with space before dash

## File Structure

```
rainbow_report_verification/
├── report_analyzer.py    # Main analyzer script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Requirements

- Python 3.6+
- pdfplumber

## Notes

- The tool validates **61 different test parameters** per report
- Supports **single PDFs, directories, and ZIP files**
- **ZIP Mode**: Only displays detailed reports for abnormal cases (clean reports show summary only)
- **Smart Output**: Automatically adapts based on number of files and findings
- Handles duplicate filenames across different folders in ZIP files
- All values are cross-checked against their specific reference ranges
- Results are grouped by category for easy review
- Automatic cleanup of temporary extraction files

## Troubleshooting

**Path not found:**
- Try using relative paths like `../report/folder`
- Remove quotes around paths if copy-pasted
- Check that the PDF file exists and is readable

**No values parsed:**
- Ensure the PDF format matches the expected neonatal screening report structure
- Check that the PDF contains text (not just scanned images)

## Author

Built for neonatal screening report verification and quality assurance.
