# Shared Utilities

This folder contains shared utility scripts that can be used across multiple skills.

## Available Utilities

### `md_to_pdf.py` - Markdown to PDF Converter

Converts Markdown files to PDF format with support for tables, code blocks, and Unicode characters.

#### Usage

```bash
# From any skill directory
python ../utils/md_to_pdf.py "path/to/file.md"

# Or from project root
python utils/md_to_pdf.py "skill_name/analyses/report.md"
```

#### Features
- Converts Markdown to HTML using Python `markdown` library
- Renders HTML to PDF using `xhtml2pdf`
- Supports tables, code blocks, emphasis, and headers
- Unicode error handling for non-ASCII characters (Chinese, emojis, etc.)
- Automatic output filename generation (replaces `.md` with `.pdf`)

#### Dependencies
```bash
pip install markdown xhtml2pdf
```

#### Used By
- `stock_analysis_skill` - Convert stock analysis reports to PDF
- `ercot_analysis_skill` - Convert ERCOT analysis reports to PDF
- `trades_analysis_skill` - Convert trading analysis reports to PDF

---

## Adding New Utilities

When adding new shared utilities:
1. Place the script in this `utils/` folder
2. Document it in this README with usage examples
3. List which skills use the utility
4. Update skill documentation to reference the shared utility
