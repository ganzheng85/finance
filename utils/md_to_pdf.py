"""
Convert markdown file to PDF using markdown-pdf
"""
from markdown_pdf import MarkdownPdf, Section
from pathlib import Path
import sys

def convert_md_to_pdf(md_file, pdf_file=None):
    """Convert markdown file to PDF"""

    # Read markdown file
    md_path = Path(md_file)
    if not md_path.exists():
        try:
            print(f"Error: File {md_file} not found")
        except UnicodeEncodeError:
            print("Error: File not found")
        return False

    # Default output file
    if pdf_file is None:
        pdf_file = md_path.with_suffix('.pdf')

    # Convert to PDF
    try:
        print(f"Converting {md_path.name} to PDF...")
    except UnicodeEncodeError:
        print("Converting markdown file to PDF...")

    try:
        # Initialize the PDF writer
        pdf = MarkdownPdf(toc_level=2)

        # Read markdown content
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Add content as a section and save
        pdf.add_section(Section(md_content))
        pdf.save(str(pdf_file))

        try:
            print(f"[SUCCESS] PDF created successfully: {pdf_file}")
        except UnicodeEncodeError:
            print("[SUCCESS] PDF created successfully")
        return True

    except Exception as e:
        print(f"[ERROR] Conversion failed: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_to_pdf.py <markdown_file> [output_pdf_file]")
        sys.exit(1)

    md_file = sys.argv[1]
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_md_to_pdf(md_file, pdf_file)
