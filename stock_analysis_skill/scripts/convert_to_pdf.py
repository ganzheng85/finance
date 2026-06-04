#!/usr/bin/env python3
"""
Convert Markdown analysis to PDF

Usage:
    python convert_to_pdf.py input.md output.pdf
"""

import sys
import markdown
from weasyprint import HTML, CSS
from pathlib import Path


def markdown_to_pdf(input_path: str, output_path: str):
    """Convert markdown file to PDF with nice formatting."""

    # Read markdown file
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'nl2br']
    )

    # Add CSS styling for better PDF appearance
    css_style = """
    @page {
        size: Letter;
        margin: 0.75in;
    }

    body {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
    }

    h1 {
        color: #1a1a1a;
        font-size: 24pt;
        border-bottom: 3px solid #0066cc;
        padding-bottom: 8px;
        margin-top: 24px;
        margin-bottom: 16px;
    }

    h2 {
        color: #0066cc;
        font-size: 18pt;
        margin-top: 20px;
        margin-bottom: 12px;
        border-bottom: 1px solid #ccc;
        padding-bottom: 4px;
    }

    h3 {
        color: #333;
        font-size: 14pt;
        margin-top: 16px;
        margin-bottom: 8px;
    }

    h4 {
        color: #555;
        font-size: 12pt;
        margin-top: 12px;
        margin-bottom: 6px;
    }

    table {
        border-collapse: collapse;
        width: 100%;
        margin: 12px 0;
        font-size: 10pt;
    }

    th {
        background-color: #0066cc;
        color: white;
        padding: 8px;
        text-align: left;
        font-weight: bold;
    }

    td {
        border: 1px solid #ddd;
        padding: 8px;
    }

    tr:nth-child(even) {
        background-color: #f9f9f9;
    }

    strong {
        color: #000;
        font-weight: 600;
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
        border-top: 2px solid #ddd;
        margin: 20px 0;
    }

    blockquote {
        border-left: 4px solid #0066cc;
        padding-left: 16px;
        margin: 12px 0;
        color: #555;
        font-style: italic;
    }

    code {
        background-color: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 9pt;
    }
    """

    # Wrap HTML content with proper structure
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Stock Analysis Report</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Convert to PDF
    HTML(string=full_html).write_pdf(
        output_path,
        stylesheets=[CSS(string=css_style)]
    )

    print(f"✓ PDF created successfully: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_to_pdf.py input.md output.pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    markdown_to_pdf(input_file, output_file)
