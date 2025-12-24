#!/usr/bin/env python3
"""
Neonatal Screening Report Analyzer
Reads PDF reports, validates values against reference ranges, and flags abnormalities.
"""

import re
import sys
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber not installed. Please run: pip install pdfplumber")
    sys.exit(1)


class NeonatalReportAnalyzer:
    """Analyzes neonatal screening reports from PDF files."""

    def __init__(self, pdf_path: str, relative_path: str = None):
        """Initialize with path to PDF file."""
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Store relative path for display (e.g., "HYDERABAD/BABY OF X.pdf")
        self.relative_path = relative_path or self.pdf_path.name

        self.patient_info = {}
        self.biochemical_params = []
        self.amino_acids = []
        self.amino_acid_ratios = []
        self.acylcarnitines = []
        self.acylcarnitine_ratios = []
        self.raw_text = ""
        self.abnormalities = []  # Track all abnormal findings

    def extract_text_from_pdf(self, quiet: bool = False) -> str:
        """Extract all text from PDF."""
        if not quiet:
            print(f"\n{'='*80}")
            print(f"Reading PDF: {self.pdf_path.name}")
            print(f"{'='*80}\n")

        all_text = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                if not quiet:
                    print(f"Total pages: {len(pdf.pages)}\n")
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    all_text.append(f"\n--- PAGE {i} ---\n{text}")
                    if not quiet:
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

    def parse_biochemical_parameters(self):
        """Parse biochemical parameters from Page 1."""
        text = self.raw_text

        # List of biochemical parameters to look for
        params = ['TSH(CH)', '17-OHP (CAH)', 'G-6PD', 'TGAL', 'BIOTINDASE',
                  'PHENYLALANINE', 'IRT']

        for param in params:
            # Try to find the parameter and its result
            pattern = rf'{re.escape(param)}\s+(\w+)'
            match = re.search(pattern, text)
            if match:
                result = match.group(1).strip()
                self.biochemical_params.append({
                    'parameter': param,
                    'result': result,
                    'method': 'Fluoroimmunoassay' if 'TSH' in param or '17-OHP' in param or 'IRT' in param else 'Enzyme Assay'
                })

    def parse_amino_acids(self):
        """Parse amino acids table from Page 2."""
        text = self.raw_text

        # Define amino acids in order as they appear in the table
        amino_acids_list = [
            'ALANINE', 'ARGININE', 'ASPARTIC ACID', 'CITRULINE',
            'GLUTAMIC ACID', 'GLYCINE', 'LEUCINE', 'METHIONINE',
            'ORNITHINE', 'PHENYLALANINE', 'PROLINE', 'TYROSINE', 'VALINE'
        ]

        for aa in amino_acids_list:
            # Pattern: AMINO_ACID_NAME followed by numeric value and range
            # Example: ALANINE 328.4 72.5-816
            pattern = rf'{aa}\s+([\d.]+)\s+([\d.<>\-]+)'
            match = re.search(pattern, text)
            if match:
                value = match.group(1).strip()
                ref_range = match.group(2).strip()
                self.amino_acids.append({
                    'analyte': aa,
                    'value': float(value),
                    'reference_range': ref_range,
                    'unit': 'uM'
                })

    def parse_amino_acid_ratios(self):
        """Parse amino acid molar ratios from Page 2."""
        text = self.raw_text

        # Define ratios in order
        ratios_list = ['MET/LEU', 'MET/PHE', 'PKU', 'LEU/ALA', 'LEU/TYR']

        for ratio in ratios_list:
            # Pattern: RATIO value range
            # Example: MET/LEU 0.11 <0.42
            pattern = rf'{re.escape(ratio)}\s+([\d.]+)\s+([<>\d.\-]+)'
            match = re.search(pattern, text)
            if match:
                value = match.group(1).strip()
                ref_range = match.group(2).strip()
                self.amino_acid_ratios.append({
                    'ratio': ratio,
                    'value': float(value),
                    'reference_range': ref_range
                })

    def parse_acylcarnitines(self):
        """Parse acylcarnitines from Page 3."""
        text = self.raw_text

        # Define acylcarnitines in order
        acyl_list = [
            'TOTAL CARNITINES', 'FREE CARNITINE', 'ACYLCARNITINES', 'AC/TC',
            'C2', 'C3', 'C4', 'C4OH/C3DC', 'C5', 'C5:1', 'C5DC', 'C5OH/C4DC',
            'C6', 'C6DC', 'C8', 'C10', 'C10:1', 'C10:2', 'C12', 'C12:1',
            'C14', 'C14:1', 'C14:2', 'C14OH', 'C16', 'C16:1', 'C16:1OH', 'C16OH',
            'C18', 'C18:1', 'C18:1OH', 'C18:2', 'C8:1'
        ]

        for acyl in acyl_list:
            # Pattern: ANALYTE value range
            # Handle ranges with spaces like "0.00 - 0.5" or "0.00 -0.429"
            # Example: C2 8.583 1.26-88
            pattern = rf'{re.escape(acyl)}\s+([\d.]+)\s+([\d.<>\s\-]+?)(?:\s+\d+\s+|\n|$)'
            match = re.search(pattern, text)
            if match:
                value = match.group(1).strip()
                ref_range = match.group(2).strip()
                self.acylcarnitines.append({
                    'analyte': acyl,
                    'value': float(value),
                    'reference_range': ref_range,
                    'unit': 'uM'
                })

    def parse_acylcarnitine_ratios(self):
        """Parse acylcarnitine molar ratios from Page 3."""
        text = self.raw_text

        # Define ratios
        ratios_list = [
            'C4/C3', 'C3/C0', 'C3/C2', 'C8/C10', 'C8/C2',
            'C0/(C16+C18)', 'C5/C2', 'C5/C3', 'C5DC/C3', 'C5DC/C16'
        ]

        for ratio in ratios_list:
            # Pattern: RATIO value range
            # Handle special characters in ratio names
            pattern = rf'{re.escape(ratio)}\s+([\d.]+)\s+([<>\d.\-]+)'
            match = re.search(pattern, text)
            if match:
                value = match.group(1).strip()
                ref_range = match.group(2).strip()
                self.acylcarnitine_ratios.append({
                    'ratio': ratio,
                    'value': float(value),
                    'reference_range': ref_range
                })

    def parse_reference_range(self, range_str: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Parse reference range string into min and max values.

        Formats supported:
        - "<3.00" -> (None, 3.0)
        - ">5.0" -> (5.0, None)
        - "0.9-45" -> (0.9, 45.0)
        - "0-1256" -> (0.0, 1256.0)
        - "72.5-816" -> (72.5, 816.0)
        - "0.00 - 0.5" -> (0.0, 0.5)
        - "0.00 -0.429" -> (0.0, 0.429)

        Returns: (min_value, max_value) where None means no limit
        """
        range_str = range_str.strip()

        # Handle < (less than - only upper limit)
        if range_str.startswith('<'):
            max_val = float(range_str[1:].strip())
            return (None, max_val)

        # Handle > (greater than - only lower limit)
        if range_str.startswith('>'):
            min_val = float(range_str[1:].strip())
            return (min_val, None)

        # Handle range with dash (e.g., "0.9-45" or "0.00 - 0.5")
        if '-' in range_str:
            # Remove spaces around dash for easier parsing
            normalized = range_str.replace(' ', '')

            # Now split on dash
            parts = normalized.split('-')

            # Filter out empty strings
            parts = [p for p in parts if p]

            if len(parts) == 2:
                try:
                    min_val = float(parts[0])
                    max_val = float(parts[1])
                    return (min_val, max_val)
                except ValueError:
                    pass
            elif len(parts) == 3:
                # Could be negative number at start (e.g., "-5-10")
                try:
                    if normalized.startswith('-'):
                        min_val = float('-' + parts[0])
                        max_val = float(parts[1])
                        return (min_val, max_val)
                except ValueError:
                    pass

        # Single value (treat as exact or use as upper limit)
        try:
            val = float(range_str)
            return (None, val)
        except ValueError:
            return (None, None)

    def is_value_in_range(self, value: float, range_str: str) -> Tuple[bool, str]:
        """
        Check if a value is within the reference range.

        Returns: (is_normal, reason)
        """
        min_val, max_val = self.parse_reference_range(range_str)

        # If we couldn't parse the range, assume normal
        if min_val is None and max_val is None:
            return (True, "Could not parse range")

        # Check lower bound
        if min_val is not None and value < min_val:
            return (False, f"Below minimum ({min_val})")

        # Check upper bound
        if max_val is not None and value > max_val:
            return (False, f"Above maximum ({max_val})")

        return (True, "Within range")

    def validate_all_values(self):
        """Validate all parsed values against their reference ranges."""
        self.abnormalities = []

        # Validate amino acids
        for aa in self.amino_acids:
            is_normal, reason = self.is_value_in_range(aa['value'], aa['reference_range'])
            aa['is_normal'] = is_normal
            aa['validation_reason'] = reason

            if not is_normal:
                self.abnormalities.append({
                    'category': 'Amino Acid',
                    'analyte': aa['analyte'],
                    'value': aa['value'],
                    'reference_range': aa['reference_range'],
                    'reason': reason,
                    'unit': aa.get('unit', '')
                })

        # Validate amino acid ratios
        for ratio in self.amino_acid_ratios:
            is_normal, reason = self.is_value_in_range(ratio['value'], ratio['reference_range'])
            ratio['is_normal'] = is_normal
            ratio['validation_reason'] = reason

            if not is_normal:
                self.abnormalities.append({
                    'category': 'Amino Acid Ratio',
                    'analyte': ratio['ratio'],
                    'value': ratio['value'],
                    'reference_range': ratio['reference_range'],
                    'reason': reason,
                    'unit': ''
                })

        # Validate acylcarnitines
        for acyl in self.acylcarnitines:
            is_normal, reason = self.is_value_in_range(acyl['value'], acyl['reference_range'])
            acyl['is_normal'] = is_normal
            acyl['validation_reason'] = reason

            if not is_normal:
                self.abnormalities.append({
                    'category': 'Acylcarnitine',
                    'analyte': acyl['analyte'],
                    'value': acyl['value'],
                    'reference_range': acyl['reference_range'],
                    'reason': reason,
                    'unit': acyl.get('unit', '')
                })

        # Validate acylcarnitine ratios
        for ratio in self.acylcarnitine_ratios:
            is_normal, reason = self.is_value_in_range(ratio['value'], ratio['reference_range'])
            ratio['is_normal'] = is_normal
            ratio['validation_reason'] = reason

            if not is_normal:
                self.abnormalities.append({
                    'category': 'Acylcarnitine Ratio',
                    'analyte': ratio['ratio'],
                    'value': ratio['value'],
                    'reference_range': ratio['reference_range'],
                    'reason': reason,
                    'unit': ''
                })

    def print_validation_summary(self):
        """Print a comprehensive summary of validation results."""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)

        total_tests = (len(self.amino_acids) + len(self.amino_acid_ratios) +
                      len(self.acylcarnitines) + len(self.acylcarnitine_ratios))

        num_abnormal = len(self.abnormalities)
        num_normal = total_tests - num_abnormal

        print(f"Total Tests Performed: {total_tests}")
        print(f"Normal Results: {num_normal}")
        print(f"Abnormal Results: {num_abnormal}")

        if num_abnormal == 0:
            print("\n✓ ALL VALUES ARE WITHIN NORMAL RANGE")
        else:
            print(f"\n⚠️  {num_abnormal} ABNORMALITY(IES) DETECTED")

        print("="*80)

    def print_abnormalities_report(self):
        """Print detailed report of all abnormalities found."""
        if not self.abnormalities:
            print("\n" + "="*80)
            print("ABNORMALITIES REPORT")
            print("="*80)
            print("✓ No abnormalities detected. All values are within normal range.")
            print("="*80)
            return

        print("\n" + "="*80)
        print(f"⚠️  ABNORMALITIES REPORT - {len(self.abnormalities)} ISSUE(S) FOUND")
        print("="*80)

        # Group by category
        categories = {}
        for abn in self.abnormalities:
            cat = abn['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(abn)

        # Print by category
        for category, abnorms in categories.items():
            print(f"\n{category} Abnormalities ({len(abnorms)}):")
            print("-" * 80)

            for abn in abnorms:
                unit_str = f" {abn['unit']}" if abn['unit'] else ""
                print(f"  ⚠️  {abn['analyte']:<25}")
                print(f"      Value: {abn['value']}{unit_str}")
                print(f"      Reference Range: {abn['reference_range']}{unit_str}")
                print(f"      Issue: {abn['reason']}")
                print()

        print("="*80)


def extract_zip_file(zip_path: Path) -> Tuple[Path, List[Path]]:
    """
    Extract ZIP file to temporary directory and find all PDFs.

    Returns: (temp_dir_path, list_of_pdf_paths_with_relative_paths)
    """
    print(f"\nExtracting ZIP file: {zip_path.name}")

    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="neonatal_reports_"))

    try:
        # Extract ZIP
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Find all PDFs recursively
        pdf_files = []
        for pdf_path in temp_dir.rglob("*.pdf"):
            # Calculate relative path from temp_dir
            rel_path = pdf_path.relative_to(temp_dir)
            pdf_files.append((pdf_path, str(rel_path)))

        print(f"Found {len(pdf_files)} PDF file(s) in ZIP")

        # Group by folder for display
        folders = {}
        for _, rel_path in pdf_files:
            folder = str(Path(rel_path).parent)
            if folder == '.':
                folder = 'root'
            folders[folder] = folders.get(folder, 0) + 1

        for folder, count in sorted(folders.items()):
            print(f"  - {folder}: {count} PDF(s)")

        return temp_dir, pdf_files

    except Exception as e:
        # Clean up on error
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(f"Error extracting ZIP file: {e}")


def process_batch_pdfs(pdf_files: List[Tuple[Path, str]], show_all: bool = False) -> Dict:
    """
    Process multiple PDFs and return summary statistics.

    Args:
        pdf_files: List of (absolute_path, relative_path) tuples
        show_all: If True, show all reports. If False, only show abnormal ones.

    Returns: Dictionary with statistics and results
    """
    results = {
        'total': len(pdf_files),
        'successful': 0,
        'failed': 0,
        'normal': 0,
        'abnormal': 0,
        'abnormal_reports': [],
        'normal_reports': [],
        'failed_reports': []
    }

    print(f"\n{'='*80}")
    print(f"PROCESSING {len(pdf_files)} PDF FILE(S)")
    print(f"{'='*80}\n")

    for idx, (pdf_path, rel_path) in enumerate(pdf_files, 1):
        try:
            print(f"[{idx}/{len(pdf_files)}] Processing: {rel_path}...", end=" ", flush=True)

            analyzer = NeonatalReportAnalyzer(str(pdf_path), rel_path)
            analyzer.extract_text_from_pdf(quiet=True)  # Quiet mode for batch processing
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
                print(f"⚠️  {len(analyzer.abnormalities)} abnormality(ies) found")
            else:
                results['normal'] += 1
                results['normal_reports'].append(analyzer)
                print(f"✓ Normal")

        except Exception as e:
            results['failed'] += 1
            results['failed_reports'].append({
                'path': rel_path,
                'error': str(e)
            })
            print(f"✗ Failed: {e}")

    return results


def print_batch_summary(results: Dict, source_name: str):
    """Print summary of batch processing results."""
    print("\n" + "="*80)
    print("BATCH ANALYSIS SUMMARY")
    print("="*80)
    print(f"Source: {source_name}")
    print(f"Total PDFs Found: {results['total']}")
    print(f"Successfully Processed: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print()
    print(f"Reports with Abnormalities: {results['abnormal']}")
    print(f"Reports Normal: {results['normal']}")
    print("="*80)

    # Show failed reports if any
    if results['failed'] > 0:
        print("\nFAILED REPORTS:")
        print("-" * 80)
        for failed in results['failed_reports']:
            print(f"  ✗ {failed['path']}")
            print(f"    Error: {failed['error']}")
        print()

    # Show abnormal reports index
    if results['abnormal'] > 0:
        print("\nREPORTS WITH ABNORMALITIES:")
        print("-" * 80)
        for idx, analyzer in enumerate(results['abnormal_reports'], 1):
            print(f"  {idx}. {analyzer.relative_path} - {len(analyzer.abnormalities)} abnormality(ies)")
        print("="*80)
    else:
        print("\n" + "🎉 " * 20)
        print("✓ ALL REPORTS ARE CLEAN! NO ABNORMALITIES DETECTED!")
        print("🎉 " * 20)
        print("="*80)


def print_detailed_report(analyzer: NeonatalReportAnalyzer):
    """Print detailed report for a single analyzer."""
    print("\n" + "="*80)
    print(f"DETAILED REPORT: {analyzer.relative_path}")
    print("="*80)

    # Patient info
    print("\nPATIENT INFORMATION:")
    print("-" * 80)
    for key, value in analyzer.patient_info.items():
        print(f"{key.upper().replace('_', ' ')}: {value}")

    # Validation summary
    total_tests = (len(analyzer.amino_acids) + len(analyzer.amino_acid_ratios) +
                  len(analyzer.acylcarnitines) + len(analyzer.acylcarnitine_ratios))
    num_abnormal = len(analyzer.abnormalities)

    print(f"\nVALIDATION SUMMARY:")
    print("-" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Normal: {total_tests - num_abnormal}")
    print(f"Abnormal: {num_abnormal}")

    # Print abnormalities report
    analyzer.print_abnormalities_report()


def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("NEONATAL SCREENING REPORT ANALYZER")
    print("="*80)

    # Get file path from user
    print("\nEnter file path:")
    print("  - Single PDF file")
    print("  - Directory containing PDFs")
    print("  - ZIP file containing PDFs")
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

    if not input_path.exists():
        print(f"\nError: Path does not exist")
        print(f"Path entered: {user_input}")
        return

    temp_dir = None
    pdf_files = []
    source_name = str(input_path.name)

    try:
        # Handle ZIP file
        if input_path.is_file() and input_path.suffix.lower() == '.zip':
            print(f"ZIP file detected: {input_path.name}")
            temp_dir, pdf_files = extract_zip_file(input_path)

            # Process all PDFs in batch
            results = process_batch_pdfs(pdf_files, show_all=False)

            # Print batch summary
            print_batch_summary(results, source_name)

            # Print detailed reports ONLY for abnormal cases
            if results['abnormal'] > 0:
                print("\n" + "="*80)
                print("DETAILED REPORTS FOR ABNORMAL CASES")
                print("="*80)

                for analyzer in results['abnormal_reports']:
                    print_detailed_report(analyzer)

        # Handle single PDF file
        elif input_path.is_file() and input_path.suffix.lower() == '.pdf':
            print(f"Single PDF file detected: {input_path.name}")

            # Process single file
            analyzer = NeonatalReportAnalyzer(str(input_path))
            analyzer.extract_text_from_pdf()
            analyzer.parse_patient_info()
            analyzer.parse_biochemical_parameters()
            analyzer.parse_amino_acids()
            analyzer.parse_amino_acid_ratios()
            analyzer.parse_acylcarnitines()
            analyzer.parse_acylcarnitine_ratios()
            analyzer.validate_all_values()

            # Print full detailed report for single file
            print_detailed_report(analyzer)

        # Handle directory
        elif input_path.is_dir():
            print(f"Directory detected: {input_path.name}")

            # Find all PDFs in directory (non-recursive for directories)
            found_pdfs = list(input_path.glob("*.pdf"))

            if not found_pdfs:
                print(f"\nNo PDF files found in directory: {input_path}")
                return

            # Convert to format expected by batch processor
            pdf_files = [(pdf, pdf.name) for pdf in found_pdfs]

            # Process all PDFs in batch
            results = process_batch_pdfs(pdf_files, show_all=False)

            # Print batch summary
            print_batch_summary(results, source_name)

            # Print detailed reports ONLY for abnormal cases
            if results['abnormal'] > 0:
                print("\n" + "="*80)
                print("DETAILED REPORTS FOR ABNORMAL CASES")
                print("="*80)

                for analyzer in results['abnormal_reports']:
                    print_detailed_report(analyzer)

        else:
            print(f"\nError: Unsupported file type")
            print(f"Please provide a PDF file, directory, or ZIP file")
            return

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up temporary directory if it was created
        if temp_dir and temp_dir.exists():
            print(f"\nCleaning up temporary files...")
            shutil.rmtree(temp_dir, ignore_errors=True)
            print("✓ Cleanup complete")


if __name__ == "__main__":
    main()
