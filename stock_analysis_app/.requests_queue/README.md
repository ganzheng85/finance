# Fundamental Analysis Request Queue

This directory contains pending requests for comprehensive fundamental analysis.

## How it Works

1. **User clicks "Fundamental Research" in web app**
   → Creates a request file: `{TICKER}_request.json`

2. **User tells Claude Code to process requests**
   → Claude Code reads all request files
   → Generates comprehensive analysis for each ticker
   → Deletes request file when complete

3. **User views completed reports in web app**
   → Refreshes page to see HTML reports

## Request File Format

```json
{
  "ticker": "AAPL",
  "timestamp": "2026-06-21T10:30:00",
  "status": "pending"
}
```

## Processing Requests

In Claude Code, type:
```
Process fundamental analysis requests
```

This will generate comprehensive reports for all pending tickers in the queue.
