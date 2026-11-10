#!/usr/bin/env python3
"""Antigravity CLI Adapter for TradingAgents.

Executes the TradingAgents multi-agent pipeline and formats the results
directly into clean Markdown/JSON for Antigravity agents and users.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

# Force stable HTTP/1.1 to avoid Windows HTTP/2 connection reset (WinError 10054)
os.environ["HTTPCORE_NO_HTTP2"] = "1"

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

# Ensure package root is in path
ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")
load_dotenv()

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.dataflows.date_window import get_current_date
from tradingagents.dataflows.symbols import normalize_symbol


def parse_args():
    parser = argparse.ArgumentParser(description="Run TradingAgents Multi-Agent Analysis for Antigravity")
    parser.add_argument("--ticker", "-t", required=True, help="Stock / Crypto / Forex ticker (e.g. NVDA, AAPL, RELIANCE.NS, BTC-USD)")
    parser.add_argument("--date", "-d", default=None, help="Analysis date (YYYY-MM-DD). Defaults to current trading day.")
    parser.add_argument("--quick-provider", default=None, help="Provider for analyst tier (e.g. google, ollama, openai)")
    parser.add_argument("--quick-llm", default=None, help="Model ID for analyst tier (e.g. gemini-2.5-flash, qwen2.5:8b)")
    parser.add_argument("--deep-provider", default=None, help="Provider for debate/decision tier (e.g. google, ollama, openai)")
    parser.add_argument("--deep-llm", default=None, help="Model ID for debate/decision tier (e.g. gemini-2.5-pro, deepseek-r1:14b)")
    parser.add_argument("--analysts", default="market,fundamentals,news,social", help="Comma-separated analysts to include")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of markdown")
    return parser.parse_args()


def main():
    args = parse_args()
    ticker = normalize_symbol(args.ticker)
    trade_date = args.date or get_current_date()
    if isinstance(trade_date, datetime.date):
        trade_date = trade_date.strftime("%Y-%m-%d")

    config = DEFAULT_CONFIG.copy()

    # Apply tiered model config
    if args.quick_provider:
        config["quick_think_provider"] = args.quick_provider
    if args.quick_llm:
        config["quick_think_llm"] = args.quick_llm
    if args.deep_provider:
        config["deep_think_provider"] = args.deep_provider
    if args.deep_llm:
        config["deep_think_llm"] = args.deep_llm

    # Default to Google Gemini 3.5 Flash Lite if no overrides (avoids 20 RPD free tier limit on 3.5 Flash)
    if not config.get("quick_think_provider"):
        config["quick_think_provider"] = "google"
        config["quick_think_llm"] = "gemini-3.5-flash-lite"
    if not config.get("deep_think_provider"):
        config["deep_think_provider"] = "google"
        config["deep_think_llm"] = "gemini-3.5-flash-lite"

    config["llm_provider"] = config["quick_think_provider"]
    config.setdefault("llm_max_retries", 5)

    # Multi-Key Quota Optimization:
    # If a secondary Gemini key is provided, distribute keys across tiers
    # to avoid rate-limiting between parallel analysts and deep debate.
    key1 = os.environ.get("GOOGLE_API_KEY")
    key2 = os.environ.get("GOOGLE_API_KEY_SECONDARY")
    if key1 and key2 and config.get("quick_think_provider") == "google" and config.get("deep_think_provider") == "google":
        print(f"[*] Dual-Key optimization enabled: Distributing API load across both Gemini keys.")
        config["quick_think_api_key"] = key1
        config["deep_think_api_key"] = key2

    analyst_list = [a.strip() for a in args.analysts.split(",") if a.strip()]

    print(f"[*] Initializing TradingAgents Multi-Agent Graph for {ticker} as of {trade_date}...")
    print(f"[*] Quick-Think Tier (Analysts): {config.get('quick_think_provider')} ({config.get('quick_think_llm')})")
    print(f"[*] Deep-Think Tier (Debate & CIO): {config.get('deep_think_provider')} ({config.get('deep_think_llm')})")

    try:
        graph = TradingAgentsGraph(
            selected_analysts=analyst_list,
            debug=False,
            config=config,
        )
        final_state, signal = graph.propagate(ticker, trade_date)
        report_file = graph.save_reports(final_state, ticker)
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        output_data = {
            "ticker": ticker,
            "trade_date": trade_date,
            "signal": signal,
            "report_path": str(report_file),
            "final_trade_decision": final_state.get("final_trade_decision", ""),
            "trader_investment_plan": final_state.get("trader_investment_plan", ""),
            "investment_plan": final_state.get("investment_plan", ""),
            "market_report": final_state.get("market_report", ""),
        }
        print(json.dumps(output_data, indent=2, default=str))
        return

    # Print Formatted Markdown
    decision = final_state.get("final_trade_decision") or "No final trade decision produced."
    trader_plan = final_state.get("trader_investment_plan") or ""
    investment_plan = final_state.get("investment_plan") or ""

    print("\n" + "=" * 60)
    print(f"# TradingAgents Decision Report: {ticker}")
    print(f"**Date:** {trade_date} | **Consensus Signal:** `{signal}`")
    print(f"**Full Artifact:** `{report_file}`")
    print("=" * 60)

    if decision:
        print(f"\n### 🏛️ Portfolio Manager & CIO Decision")
        print(decision)

    if trader_plan:
        print(f"\n### 🎯 Trading Team Order Specification")
        print(trader_plan)

    if investment_plan:
        print(f"\n### ⚖️ Research & Investment Thesis")
        print(investment_plan)

    for analyst_key, heading in [
        ("market_report", "Market / Technical Analysis"),
        ("fundamentals_report", "Fundamentals Analysis"),
        ("news_report", "News & Catalysts"),
        ("sentiment_report", "Social & Sentiment Analysis"),
    ]:
        val = final_state.get(analyst_key)
        if val:
            print(f"\n### 📊 {heading}")
            print(val)

    print("\n" + "=" * 60)
    print(f"Report complete. Both Markdown and HTML artifacts saved to:\n  {report_file.parent}")


if __name__ == "__main__":
    main()
