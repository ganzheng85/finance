"""
Convert markdown file to HTML with professional styling
"""
import markdown
from pathlib import Path
import sys

def convert_md_to_html(md_file, html_file=None):
    """Convert markdown file to HTML"""

    # Read markdown file
    md_path = Path(md_file)
    if not md_path.exists():
        try:
            print(f"Error: File {md_file} not found")
        except UnicodeEncodeError:
            print("Error: File not found")
        return False

    # Default output file
    if html_file is None:
        html_file = md_path.with_suffix('.html')

    # Read markdown content
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML with extensions
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'nl2br', 'toc']
    )

    # Add CSS styling
    css_style = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background-color: white;
            padding: 40px 50px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        h1 {
            color: #003d7a;
            font-size: 28px;
            border-bottom: 3px solid #003d7a;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }

        h2 {
            color: #005a9c;
            font-size: 22px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 8px;
            margin-top: 30px;
            margin-bottom: 15px;
        }

        h3 {
            color: #0066b3;
            font-size: 18px;
            margin-top: 20px;
            margin-bottom: 10px;
        }

        h4 {
            color: #444;
            font-size: 16px;
            margin-top: 15px;
            margin-bottom: 8px;
        }

        p {
            margin: 12px 0;
            text-align: justify;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 13px;
        }

        th {
            background-color: #003d7a;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: 600;
            border: 1px solid #002855;
        }

        td {
            padding: 8px 10px;
            border: 1px solid #ddd;
        }

        tbody tr:nth-child(even) {
            background-color: #f9f9f9;
        }

        tbody tr:hover {
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
            margin: 12px 0;
            padding-left: 30px;
        }

        li {
            margin: 6px 0;
        }

        hr {
            border: none;
            border-top: 1px solid #ccc;
            margin: 25px 0;
        }

        code {
            background-color: #f5f5f5;
            padding: 3px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: #c7254e;
        }

        pre {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 15px 0;
        }

        pre code {
            background-color: transparent;
            padding: 0;
        }

        blockquote {
            border-left: 4px solid #005a9c;
            padding-left: 15px;
            margin: 15px 0;
            color: #555;
            font-style: italic;
        }

        @media print {
            body {
                background-color: white;
                padding: 0;
            }

            .container {
                box-shadow: none;
                padding: 20px;
            }

            .no-print {
                display: none;
            }
        }

        .print-button {
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #003d7a;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }

        .print-button:hover {
            background-color: #005a9c;
        }
    """

    # Create full HTML document
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Analysis Report</title>
    <style>{css_style}</style>
</head>
<body>
    <button class="print-button no-print" onclick="window.print()">🖨️ Print / Save as PDF</button>
    <div class="container">
        {html_content}
    </div>
</body>
</html>
"""

    # Write HTML file
    try:
        print(f"Converting {md_path.name} to HTML...")
    except UnicodeEncodeError:
        print("Converting markdown file to HTML...")

    try:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(full_html)

        try:
            print(f"[SUCCESS] HTML created successfully: {html_file}")
        except UnicodeEncodeError:
            print("[SUCCESS] HTML created successfully")
        return True

    except Exception as e:
        print(f"[ERROR] Conversion failed: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python md_to_html.py <markdown_file> [output_html_file]")
        sys.exit(1)

    md_file = sys.argv[1]
    html_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_md_to_html(md_file, html_file)
