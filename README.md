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

## Output

The analyzer produces:

1. **Patient Information**: Demographics and test dates
2. **Biochemical Parameters**: NORMAL/ABNORMAL status for each parameter
3. **Detailed Test Results**: All analytes with values, reference ranges, and validation status
4. **Validation Summary**: Total tests, normal/abnormal counts
5. **Abnormalities Report**: Detailed breakdown of any issues found

### Example Output

```
================================================================================
VALIDATION SUMMARY
================================================================================
Total Tests Performed: 61
Normal Results: 61
Abnormal Results: 0

✓ ALL VALUES ARE WITHIN NORMAL RANGE
================================================================================

================================================================================
ABNORMALITIES REPORT
================================================================================
✓ No abnormalities detected. All values are within normal range.
================================================================================
```

If abnormalities are detected:

```
================================================================================
⚠️  ABNORMALITIES REPORT - 2 ISSUE(S) FOUND
================================================================================

Acylcarnitine Abnormalities (2):
--------------------------------------------------------------------------------
  ⚠️  C4OH/C3DC
      Value: 0.032 uM
      Reference Range: 0.00 - 0.5 uM
      Issue: Above maximum (0.5)

  ⚠️  C5DC
      Value: 0.037 uM
      Reference Range: 0.00 -0.429 uM
      Issue: Above maximum (0.429)
================================================================================
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
- Handles both single files and batch processing of directories
- All values are cross-checked against their specific reference ranges
- Results are grouped by category for easy review

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
