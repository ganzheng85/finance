# MD to PDF Migration Notes

## Date: June 12, 2026

## Summary
Consolidated duplicate `md_to_pdf.py` scripts into a shared utility to promote code reuse across skills.

## Changes Made

### 1. Created Shared Utility
- **Location**: `utils/md_to_pdf.py`
- **Source**: Copied from `stock_analysis_skill/scripts/md_to_pdf.py` (better version with Unicode handling)
- **Features**: 
  - Markdown to PDF conversion
  - Unicode error handling (for Chinese characters, emojis, etc.)
  - Support for tables, code blocks, headers

### 2. Removed Duplicate Scripts
Deleted the following duplicate files:
- ✅ `stock_analysis_skill/scripts/md_to_pdf.py` (replaced by shared utility)
- ✅ `ercot_analysis_skill/scripts/md_to_pdf.py` (replaced by shared utility)

### 3. Updated Documentation
Updated references to use shared utility:
- ✅ `stock_analysis_skill/README.md` - Updated usage examples
- ✅ `stock_analysis_skill/SKILL.md` - Updated workflow step 7
- ✅ Created `utils/README.md` - Documentation for shared utilities

### 4. Usage Examples

**From project root:**
```bash
python utils/md_to_pdf.py "stock_analysis_skill/analyses/AVGO/AVGO-2026-06-09.md"
```

**From within a skill directory:**
```bash
cd stock_analysis_skill
python ../utils/md_to_pdf.py "analyses/AVGO/AVGO-2026-06-09.md"
```

### 5. Skills That Can Use This Utility
- `stock_analysis_skill` - ✅ Updated
- `ercot_analysis_skill` - ✅ Updated (script removed, can now use shared)
- `trades_analysis_skill` - Can now use for `trading_analysis_report.md`
- Future skills - Can reuse without duplicating code

## Benefits
1. **DRY Principle**: Single source of truth for PDF conversion logic
2. **Maintainability**: Bug fixes and improvements only need to be made in one place
3. **Consistency**: All skills use the same PDF conversion logic
4. **Discoverability**: New skills can easily find and use shared utilities

## Testing
✅ Tested conversion of `AVGO-2026-06-09-Highlights.md` - SUCCESS

## Next Steps
- Other skills needing PDF conversion can now use `utils/md_to_pdf.py`
- Consider adding other common utilities to the `utils/` folder (e.g., data fetchers, formatters)
