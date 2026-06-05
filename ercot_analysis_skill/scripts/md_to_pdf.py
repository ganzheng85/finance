"""
Convert markdown file to PDF with styling
"""
import markdown
from xhtml2pdf import pisa
from pathlib import Path
import sys
import io

def convert_md_to_pdf(md_file, pdf_file=None):
    """Convert markdown file to PDF"""

    # Read markdown file
    md_path = Path(md_file)
    if not md_path.exists():
        print(f"Error: File {md_file} not found")
        return False

    # Default output file
    if pdf_file is None:
        pdf_file = md_path.with_suffix('.pdf')

    # Read markdown content
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML with extensions
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'nl2br']
    )

    # Add CSS styling
    css_style = """
        @page {
            size: letter;
            margin: 0.75in;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #333;
        }

        h1 {
            color: #003d7a;
            font-size: 24pt;
            border-bottom: 3px solid #003d7a;
            padding-bottom: 8px;
            margin-top: 0;
            margin-bottom: 20px;
        }

        h2 {
            color: #005a9c;
            font-size: 16pt;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 5px;
            margin-top: 24px;
            margin-bottom: 12px;
            page-break-after: avoid;
        }

        h3 {
            color: #0066b3;
            font-size: 12pt;
            margin-top: 16px;
            margin-bottom: 8px;
            page-break-after: avoid;
        }

        h4 {
            color: #444;
            font-size: 11pt;
            margin-top: 12px;
            margin-bottom: 6px;
        }

        p {
            margin: 8px 0;
            text-align: justify;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
            font-size: 9pt;
            page-break-inside: avoid;
        }

        th {
            background-color: #003d7a;
            color: white;
            padding: 8px 6px;
            text-align: left;
            font-weight: 600;
            border: 1px solid #002855;
        }

        td {
            padding: 6px;
            border: 1px solid #ddd;
        }

        tr:nth-child(even) {
            background-color: #f9f9f9;
        }

        tr:hover {
            background-color: #f0f8ff;
        }

        strong {
            color: #003d7a;
            font-weight: 600;
        }

        em {
            color: #555;
            font-style: italic;
        }

        ul, ol {
            margin: 8px 0;
            padding-left: 24px;
        }

        li {
            margin: 4px 0;
        }

        hr {
            border: none;
            border-top: 1px solid #ccc;
            margin: 16px 0;
        }

        code {
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            color: #c7254e;
        }

        blockquote {
            border-left: 4px solid #005a9c;
            padding-left: 12px;
            margin: 12px 0;
            color: #555;
            font-style: italic;
        }
    """

    # Convert to PDF
    print(f"Converting {md_path.name} to PDF...")

    # Create full HTML document with CSS
    full_html_with_css = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>ERCOT Market Analysis</title>
        <style>{css_style}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Write PDF
    with open(pdf_file, "w+b") as output:
        pisa_status = pisa.CreatePDF(
            full_html_with_css,
            dest=output
        )

    if pisa_status.err:
        print(f"[ERROR] Error during PDF creation: {pisa_status.err}")
        return False

    print(f"[SUCCESS] PDF created successfully: {pdf_file}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_to_pdf.py <markdown_file> [output_pdf_file]")
        sys.exit(1)

    md_file = sys.argv[1]
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_md_to_pdf(md_file, pdf_file)
