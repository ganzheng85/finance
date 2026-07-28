#!/usr/bin/env python3
"""
Simple Markdown to PDF converter using reportlab

Usage:
    python md_to_pdf_simple.py input.md output.pdf
"""

import sys
import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib import colors


def parse_markdown(md_content):
    """Simple markdown parser for basic formatting."""
    lines = md_content.split('\n')
    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=12,
        spaceBefore=12,
        borderColor=colors.HexColor('#0066cc'),
        borderWidth=2,
        borderPadding=6,
    ))

    styles.add(ParagraphStyle(
        name='CustomHeading2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#0066cc'),
        spaceAfter=10,
        spaceBefore=14,
        borderColor=colors.grey,
        borderWidth=1,
        borderPadding=4,
    ))

    styles.add(ParagraphStyle(
        name='CustomHeading3',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.black,
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold',
    ))

    i = 0
    table_data = []
    in_table = False

    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines (add small spacer)
        if not line:
            if not in_table:
                elements.append(Spacer(1, 0.1*inch))
            i += 1
            continue

        # Title (# heading)
        if line.startswith('# '):
            text = line[2:].strip()
            elements.append(Paragraph(text, styles['CustomTitle']))

        # Heading 2 (## heading)
        elif line.startswith('## '):
            text = line[3:].strip()
            elements.append(Paragraph(text, styles['CustomHeading2']))

        # Heading 3 (### heading)
        elif line.startswith('### '):
            text = line[4:].strip()
            elements.append(Paragraph(text, styles['CustomHeading3']))

        # Horizontal rule
        elif line.startswith('---'):
            elements.append(Spacer(1, 0.2*inch))

        # Table detection
        elif '|' in line and not in_table:
            # Start collecting table
            table_data = []
            in_table = True
            # Process this line as first row
            row = [cell.strip() for cell in line.split('|') if cell.strip()]
            table_data.append(row)

        elif '|' in line and in_table:
            # Check if separator row
            if all(c in '-:|' or c.isspace() for c in line):
                i += 1
                continue  # Skip separator
            row = [cell.strip() for cell in line.split('|') if cell.strip()]
            table_data.append(row)

        elif in_table and '|' not in line:
            # End of table
            if table_data:
                # Create table
                t = Table(table_data)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.2*inch))
            table_data = []
            in_table = False
            # Process current line normally
            continue

        # List items
        elif line.startswith('- ') or line.startswith('* '):
            text = '• ' + line[2:]
            # Make bold text work
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            elements.append(Paragraph(text, styles['BodyText']))

        # Numbered list
        elif re.match(r'^\d+\.\s', line):
            text = re.sub(r'^\d+\.\s', '', line)
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            elements.append(Paragraph(text, styles['BodyText']))

        # Regular paragraph
        else:
            text = line
            # Make bold text work
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            # Handle inline code (just make it italic for simplicity)
            text = re.sub(r'`(.*?)`', r'<i>\1</i>', text)
            elements.append(Paragraph(text, styles['BodyText']))

        i += 1

    # If table at end
    if in_table and table_data:
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(t)

    return elements


def markdown_to_pdf(input_path: str, output_path: str):
    """Convert markdown file to PDF."""

    # Read markdown
    with open(input_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Create PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )

    # Parse markdown to elements
    elements = parse_markdown(md_content)

    # Build PDF
    doc.build(elements)

    print(f"[OK] PDF created successfully: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python md_to_pdf_simple.py input.md output.pdf")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not Path(input_file).exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    markdown_to_pdf(input_file, output_file)
