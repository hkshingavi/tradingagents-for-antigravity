---
name: tradingagents-analyze
description: >-
  Runs a comprehensive multi-agent financial market analysis on any global ticker
  (US stocks, Indian NSE/BSE, Crypto, Forex) using the TradingAgents framework.
  Coordinates 4 parallel analysts (Fundamentals, Technicals, News, Social Sentiment),
  Bull vs. Bear adversarial debate, Risk Management team, and the Portfolio Manager.
  Configured for cost/speed optimization using a Dual-Tier LLM setup (Gemini Flash
  for fast analysis + Gemini Pro for deep debate, or local Ollama offloading).
argument-hint: "[ticker] [--date YYYY-MM-DD]"
---

# tradingagents-analyze

Run an institutional-grade multi-agent consensus analysis on any stock, cryptocurrency, forex pair, or index.

`${SKILL_DIR}` below is this skill's folder, and `${PLUGIN_DIR}` is the root of the `tradingagents-for-antigravity` plugin.

```bash
# Standard analysis on latest trading day (uses Gemini Flash + Pro hybrid)
python "${PLUGIN_DIR}/run_adapter.py" --ticker NVDA

# Analyze global stocks (e.g. Indian market, Europe, Asia)
python "${PLUGIN_DIR}/run_adapter.py" --ticker RELIANCE.NS
python "${PLUGIN_DIR}/run_adapter.py" --ticker 0700.HK

# Crypto or Forex
python "${PLUGIN_DIR}/run_adapter.py" --ticker BTC-USD
python "${PLUGIN_DIR}/run_adapter.py" --ticker EURUSD

# Analyze on a specific historical date (Point-in-Time, no look-ahead bias)
python "${PLUGIN_DIR}/run_adapter.py" --ticker AAPL --date 2026-09-01

# Offload the analyst tier to local Ollama (saving 75% cloud API quota)
python "${PLUGIN_DIR}/run_adapter.py" --ticker TSLA --quick-provider ollama --quick-llm qwen2.5:8b
```

## What it Outputs
1. **Consensus Rating:** `Buy` / `Overweight` / `Hold` / `Underweight` / `Sell`
2. **Order Proposal:** Exact target entry, stop-loss, and suggested position sizing percentage.
3. **Analyst Summaries:** Fundamental metrics (P/E, cash flow, debt), technical indicators (RSI, MACD), news catalysts, and social sentiment.
4. **Debate Synthesis:** Bull vs. Bear debate transcript and Risk Management critique.

## Execution Guardrails
- **Paper First:** By default, all recommendations are advisory.
- **Order Placement:** To place an actual trade based on this analysis, forward the generated order specification to `trader-broker` (e.g. via Alpaca MCP) and obtain the user's explicit approval.
