"""
Enhanced Markdown to PDF converter with Table of Contents and page numbers
"""
import markdown
from xhtml2pdf import pisa
from pathlib import Path
import sys
import re
from io import BytesIO


def extract_headings(md_content):
    """Extract headings from markdown content for TOC"""
    headings = []
    lines = md_content.split('\n')

    for line in lines:
        # Match ## headings (main sections)
        if line.startswith('## ') and not line.startswith('## Table of Contents'):
            heading_text = line.replace('##', '').strip()
            headings.append({
                'level': 2,
                'text': heading_text,
                'id': heading_text.lower().replace(' ', '-').replace(':', '').replace('/', '').replace("'", '')
            })

    return headings


def create_toc_html(headings):
    """Create HTML table of contents with page number placeholders"""
    toc_html = """
    <div class="toc-section">
        <h2 class="toc-title">Table of Contents</h2>
        <div class="toc-entries">
    """

    section_num = 1
    for heading in headings:
        # Skip executive summary and certain sections from numbering
        if any(skip in heading['text'].lower() for skip in ['executive summary', 'table of contents', 'appendix']):
            if 'executive summary' in heading['text'].lower():
                toc_html += f"""
                <div class="toc-entry">
                    <span class="toc-text">{heading['text']}</span>
                    <span class="toc-dots"></span>
                    <span class="toc-page"><pdf:pagenumber for="{heading['id']}"/></span>
                </div>
                """
            elif 'appendix' in heading['text'].lower():
                toc_html += f"""
                <div class="toc-entry">
                    <span class="toc-text">{heading['text']}</span>
                    <span class="toc-dots"></span>
                    <span class="toc-page"><pdf:pagenumber for="{heading['id']}"/></span>
                </div>
                """
            continue

        # For numbered sections
        toc_html += f"""
        <div class="toc-entry">
            <span class="toc-text">{section_num}. {heading['text'].split('. ', 1)[-1] if '. ' in heading['text'] else heading['text']}</span>
            <span class="toc-dots"></span>
            <span class="toc-page"><pdf:pagenumber for="{heading['id']}"/></span>
        </div>
        """
        section_num += 1

    toc_html += """
        </div>
    </div>
    <pdf:nextpage />
    """

    return toc_html


def add_heading_anchors(html_content, headings):
    """Add anchor IDs to headings for PDF navigation"""
    for heading in headings:
        # Create a pattern to match the heading
        pattern = f'<h2>{re.escape(heading["text"])}</h2>'
        replacement = f'<h2><a name="{heading["id"]}"></a>{heading["text"]}</h2>'
        html_content = html_content.replace(
            f'<h2>{heading["text"]}</h2>',
            replacement
        )

    return html_content


def convert_md_to_pdf_with_toc(md_file, pdf_file=None):
    """Convert markdown file to PDF with table of contents"""

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

    # Extract headings for TOC
    headings = extract_headings(md_content)

    # Remove existing TOC section from markdown if present
    md_content = re.sub(r'## Table of Contents.*?(?=##|\Z)', '', md_content, flags=re.DOTALL)

    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'nl2br']
    )

    # Add anchors to headings
    html_content = add_heading_anchors(html_content, headings)

    # Create TOC HTML
    toc_html = create_toc_html(headings)

    # CSS styling
    css_style = """
        @page {
            size: letter;
            margin: 0.75in;

            @frame footer {
                -pdf-frame-content: footerContent;
                bottom: 0.5in;
                margin-left: 0.75in;
                margin-right: 0.75in;
                height: 0.5in;
            }
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #333;
        }

        /* Table of Contents Styles */
        .toc-section {
            margin-bottom: 30px;
            page-break-after: always;
        }

        .toc-title {
            color: #003d7a;
            font-size: 18pt;
            border-bottom: 2px solid #003d7a;
            padding-bottom: 8px;
            margin-bottom: 20px;
        }

        .toc-entries {
            margin-left: 0;
        }

        .toc-entry {
            display: table;
            width: 100%;
            margin: 8px 0;
            font-size: 11pt;
        }

        .toc-entry .toc-text {
            display: table-cell;
            padding-right: 8px;
            width: 85%;
        }

        .toc-entry .toc-dots {
            display: table-cell;
            border-bottom: 1px dotted #999;
            width: 10%;
        }

        .toc-entry .toc-page {
            display: table-cell;
            text-align: right;
            width: 5%;
            font-weight: 600;
            color: #003d7a;
        }

        h1 {
            color: #003d7a;
            font-size: 24pt;
            border-bottom: 3px solid #003d7a;
            padding-bottom: 8px;
            margin-top: 0;
            margin-bottom: 20px;
            page-break-after: avoid;
        }

        h2 {
            color: #005a9c;
            font-size: 16pt;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 5px;
            margin-top: 24px;
            margin-bottom: 12px;
            page-break-before: avoid;
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

        #footerContent {
            text-align: center;
            font-size: 8pt;
            color: #666;
        }
    """

    # Insert TOC after the first h1 and disclaimer
    # Split content at first horizontal rule after h1
    parts = html_content.split('<hr />', 1)
    if len(parts) == 2:
        html_with_toc = parts[0] + '<hr />' + toc_html + parts[1]
    else:
        # Fallback: insert after first h1
        html_with_toc = re.sub(r'(<h1>.*?</h1>.*?<hr />)', r'\1' + toc_html, html_content, count=1, flags=re.DOTALL)

    # Create full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>{css_style}</style>
    </head>
    <body>
        {html_with_toc}

        <div id="footerContent">
            Page <pdf:pagenumber> of <pdf:pagecount>
        </div>
    </body>
    </html>
    """

    print(f"Converting {md_path.name} to PDF with table of contents...")

    # Write PDF
    with open(pdf_file, "w+b") as output:
        pisa_status = pisa.CreatePDF(
            full_html,
            dest=output,
            encoding='utf-8'
        )

    if pisa_status.err:
        print(f"[ERROR] Error during PDF creation")
        return False

    print(f"[SUCCESS] PDF created successfully: {pdf_file}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_to_pdf_with_toc.py <markdown_file> [output_pdf_file]")
        sys.exit(1)

    md_file = sys.argv[1]
    pdf_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_md_to_pdf_with_toc(md_file, pdf_file)
