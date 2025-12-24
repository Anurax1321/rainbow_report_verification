#!/usr/bin/env python3
"""
Neonatal Screening Report Analyzer
Reads PDF reports, validates values against reference ranges, and flags abnormalities.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed. Please run: pip install pdfplumber")
    sys.exit(1)


class NeonatalReportAnalyzer:
    """Analyzes neonatal screening reports from PDF files."""

    def __init__(self, pdf_path: str):
        """Initialize with path to PDF file."""
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        self.patient_info = {}
        self.biochemical_params = []
        self.amino_acids = []
        self.amino_acid_ratios = []
        self.acylcarnitines = []
        self.acylcarnitine_ratios = []
        self.raw_text = ""

    def extract_text_from_pdf(self) -> str:
        """Extract all text from PDF."""
        print(f"\n{'='*80}")
        print(f"Reading PDF: {self.pdf_path.name}")
        print(f"{'='*80}\n")

        all_text = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                print(f"Total pages: {len(pdf.pages)}\n")
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    all_text.append(f"\n--- PAGE {i} ---\n{text}")
                    print(f"Page {i} extracted ({len(text)} characters)")
        except Exception as e:
            raise RuntimeError(f"Error reading PDF: {e}")

        self.raw_text = "\n".join(all_text)
        return self.raw_text

    def parse_patient_info(self):
        """Extract patient information from the report."""
        text = self.raw_text

        # Extract patient name
        name_match = re.search(r'Patient Name\s+(.+?)(?:\n|Collected)', text)
        if name_match:
            self.patient_info['name'] = name_match.group(1).strip()

        # Extract age/gender
        age_match = re.search(r'Age/Gender\s+(.+?)(?:\n|Received)', text)
        if age_match:
            self.patient_info['age_gender'] = age_match.group(1).strip()

        # Extract UHID
        uhid_match = re.search(r'UHID\s+(.+?)(?:\n|Reported)', text)
        if uhid_match:
            self.patient_info['uhid'] = uhid_match.group(1).strip()

        # Extract Referred By
        ref_match = re.search(r'Referred By\s+(.+?)(?:\n|Reference)', text)
        if ref_match:
            self.patient_info['referred_by'] = ref_match.group(1).strip()

        # Extract dates
        collected_match = re.search(r'Collected on\s+(.+?)(?:\n|$)', text)
        if collected_match:
            self.patient_info['collected_on'] = collected_match.group(1).strip()

        received_match = re.search(r'Received on\s+(.+?)(?:\n|$)', text)
        if received_match:
            self.patient_info['received_on'] = received_match.group(1).strip()

        reported_match = re.search(r'Reported on\s+(.+?)(?:\n|$)', text)
        if reported_match:
            self.patient_info['reported_on'] = reported_match.group(1).strip()

    def print_patient_info(self):
        """Print patient information."""
        print("\n" + "="*80)
        print("PATIENT INFORMATION")
        print("="*80)
        for key, value in self.patient_info.items():
            print(f"{key.upper().replace('_', ' ')}: {value}")
        print("="*80)


def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("NEONATAL SCREENING REPORT ANALYZER")
    print("="*80)

    # Get PDF file path(s) from user
    print("\nEnter PDF file path (or directory containing PDFs):")
    print("(You can drag-and-drop the file/folder, or paste the path)")
    user_input = input("> ").strip()

    if not user_input:
        print("Error: No path provided")
        return

    # Clean up the input - remove quotes if present
    user_input = user_input.strip('"').strip("'")

    # Expand user path (~) and resolve
    input_path = Path(user_input).expanduser()

    # Debug output
    print(f"\nChecking path: {input_path}")
    print(f"Path exists: {input_path.exists()}")
    print(f"Is file: {input_path.is_file()}")
    print(f"Is directory: {input_path.is_dir()}")

    # Collect PDF files
    pdf_files = []
    if input_path.is_file() and input_path.suffix.lower() == '.pdf':
        pdf_files.append(input_path)
        print(f"Single PDF file detected: {input_path.name}")
    elif input_path.is_dir():
        pdf_files = list(input_path.glob("*.pdf"))
        if not pdf_files:
            print(f"\nNo PDF files found in directory: {input_path}")
            print(f"Directory contents:")
            try:
                for item in list(input_path.iterdir())[:10]:
                    print(f"  - {item.name}")
            except Exception as e:
                print(f"  Could not list directory: {e}")
            return
        print(f"Found PDFs in directory: {[f.name for f in pdf_files[:5]]}")
    else:
        print(f"\nError: Path does not exist or is not a PDF file")
        print(f"Path entered: {user_input}")
        print(f"Resolved path: {input_path}")
        print(f"Absolute path: {input_path.absolute()}")

        # Try to give helpful suggestions
        if not input_path.exists():
            parent = input_path.parent
            if parent.exists():
                print(f"\nParent directory exists: {parent}")
                print("Files in parent directory:")
                try:
                    for item in list(parent.iterdir())[:10]:
                        print(f"  - {item.name}")
                except:
                    pass
        return

    print(f"\nFound {len(pdf_files)} PDF file(s) to process\n")

    # Process each PDF
    for pdf_file in pdf_files:
        try:
            analyzer = NeonatalReportAnalyzer(str(pdf_file))

            # Extract text
            analyzer.extract_text_from_pdf()

            # Parse patient info
            analyzer.parse_patient_info()
            analyzer.print_patient_info()

            # CHECKPOINT: Print raw text for verification
            print("\n" + "="*80)
            print("RAW TEXT EXTRACTED (for verification)")
            print("="*80)
            print(analyzer.raw_text[:2000])  # Print first 2000 chars
            print("\n... [truncated] ...\n")

        except Exception as e:
            print(f"\nError processing {pdf_file.name}: {e}")
            continue


if __name__ == "__main__":
    main()
