---
name: tradingagents-report
description: >-
  Inspects, summarizes, or exports the comprehensive multi-agent decision reports
  and debate transcripts produced by TradingAgents. Locates HTML or Markdown artifacts
  stored under the data/results directory.
argument-hint: "[ticker] [--date YYYY-MM-DD]"
---

# tradingagents-report

View and review detailed TradingAgents reports for any previous analysis run.

`${PLUGIN_DIR}` is the root of the `tradingagents-for-antigravity` plugin.

```bash
# Locate generated reports for a ticker
python -c "import os, sys; from tradingagents.default_config import DEFAULT_CONFIG; print(DEFAULT_CONFIG['results_dir'])"
```

## Report Contents
* **Executive Summary:** Overview of the Portfolio Manager's decision.
* **Debate Transcripts:** Verbatim arguments made by the Bull and Bear Researchers.
* **Risk Management Review:** Aggressive, Neutral, and Conservative assessments.
* **Data Snapshots:** Valuation multiples, technical chart values, and news headlines captured on that date.
