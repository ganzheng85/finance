# Language Support - Chinese & English Reports

## How to Generate Chinese Reports in the Web App

The Stock Analysis Dashboard now supports both **English** and **Chinese (中文)** technical analysis reports!

### Step-by-Step Guide:

1. **Start the Web Application**
   ```bash
   cd stock_analysis_app
   python app.py
   ```
   The app will start on `http://localhost:5000`

2. **Select Your Language**
   - At the top of the page, you'll see two buttons: **English** | **中文**
   - Click **中文** to switch to Chinese
   - The entire interface will change to Chinese

3. **Check Report Language**
   - Below "Select Report Types", you'll see:
     - **English Mode**: "Report Language: English (Change using language selector above)"
     - **Chinese Mode**: "报告语言：中文（使用上方语言选择器更改）"
   
4. **Generate Your Report**
   - Enter a stock ticker (e.g., DPZ, AAPL, MSFT)
   - Check "Technical Analysis"
   - Click "Generate Reports" (or "生成报告" in Chinese)

5. **View the Report**
   - Click "📄 View Report" to open the HTML report
   - The report will be in **the language you selected** (English or Chinese)

### Language Changes:

When you switch from English to Chinese, the reports will show:

**English Report:**
```markdown
# Technical Analysis: DPZ

**Generated on:** 2026-07-12 18:05:50
**Ticker:** DPZ
**Current Price:** $299.46

## Executive Summary
**Trend Direction:** BEARISH (Strength: 6/10)
**Primary Pattern:** NEUTRAL (LOW confidence)
**Volatility Level:** HIGH

## 2. Key Technical Indicators
| Indicator | Value | Signal |
|-----------|-------|--------|
| RSI(14) | 45.45 | NEUTRAL |
| MACD Histogram | +1.0862 | BULLISH |
```

**Chinese Report (中文报告):**
```markdown
# 技术分析: DPZ

**生成时间:** 2026-07-12 18:05:50
**股票代码:** DPZ
**当前价格:** $299.46

## 执行摘要
**趋势方向:** BEARISH (强度: 6/10)
**主要形态:** NEUTRAL (LOW 置信度)
**波动水平:** HIGH

## 2. 关键技术指标
| 指标 | 数值 | 信号 |
|-----------|-------|--------|
| RSI(14) | 45.45 | 中性 |
| MACD柱状图 | +1.0862 | 看涨 |
```

### Translated Sections:

All major sections are translated:
- ✅ **Technical Analysis** → **技术分析**
- ✅ **Executive Summary** → **执行摘要**
- ✅ **Trend Analysis** → **趋势分析**
- ✅ **Key Technical Indicators** → **关键技术指标**
- ✅ **Volatility Analysis** → **波动性分析**
- ✅ **Volume Analysis** → **成交量分析**
- ✅ **Support & Resistance Levels** → **主要支撑与阻力位**
- ✅ **Trading Zones** → **交易区间**

### Technical Terms Translated:

- **Signals**: Oversold → 超卖, Overbought → 超买, Bullish → 看涨, Bearish → 看跌
- **Indicators**: RSI, MACD, ATR, ADX (same), Bollinger Bands → 布林带
- **Zones**: Support Zone → 支撑区间, Resistance Zone → 阻力区间
- **Trends**: Strong Trend → 强趋势, Weak Trend → 弱趋势

### Command Line Usage (Alternative):

You can also generate reports directly from the command line:

**English Report:**
```bash
cd technical_analysis
python scripts/analyze_stock.py DPZ --days 60 --lang en
```

**Chinese Report:**
```bash
cd technical_analysis
python scripts/analyze_stock.py DPZ --days 60 --lang zh
```

### Notes:

- The language setting is **persistent** - it's saved in your browser's localStorage
- When you refresh the page, it remembers your last language choice
- Charts are the same in both languages (prices, indicators use universal notation)
- Only the **text content** of the report changes based on language

### Troubleshooting:

**Issue**: Report is in English even though I selected Chinese
- **Solution**: Make sure the language selector shows "中文" as active (highlighted)
- Check the "Report Language" indicator shows "中文" before generating

**Issue**: Browser shows garbled Chinese characters
- **Solution**: This is a UTF-8 encoding issue. Make sure you're using a modern browser (Chrome, Firefox, Edge)

---

**Enjoy bilingual stock analysis! 享受双语股票分析！** 📈📊
