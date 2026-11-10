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

# Ensure package root is in path
ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.dataflows.date_window import latest_completed_trading_day
from tradingagents.dataflows.symbols import normalize_symbol


def parse_args():
    parser = argparse.ArgumentParser(description="Run TradingAgents Multi-Agent Analysis for Antigravity")
    parser.add_argument("--ticker", "-t", required=True, help="Stock / Crypto / Forex ticker (e.g. NVDA, AAPL, RELIANCE.NS, BTC-USD)")
    parser.add_argument("--date", "-d", default=None, help="Analysis date (YYYY-MM-DD). Defaults to latest completed trading day.")
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
    trade_date = args.date or latest_completed_trading_day()
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

    # Default to Google Gemini Flash/Pro if no overrides
    if not config.get("quick_think_provider"):
        config["quick_think_provider"] = "google"
        config["quick_think_llm"] = "gemini-2.5-flash"
    if not config.get("deep_think_provider"):
        config["deep_think_provider"] = "google"
        config["deep_think_llm"] = "gemini-2.5-pro"

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
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        output_data = {
            "ticker": ticker,
            "trade_date": trade_date,
            "signal": signal,
            "portfolio_decision": final_state.get("portfolio_decision", {}),
            "trader_proposal": final_state.get("trader_proposal", {}),
            "research_plan": final_state.get("research_plan", {}),
        }
        print(json.dumps(output_data, indent=2, default=str))
        return

    # Print Formatted Markdown
    decision = final_state.get("portfolio_decision") or {}
    trader_prop = final_state.get("trader_proposal") or {}
    research = final_state.get("research_plan") or {}

    rating = getattr(decision, "rating", signal)
    action = getattr(trader_prop, "action", "N/A")
    summary = getattr(decision, "executive_summary", "No executive summary available.")
    thesis = getattr(decision, "investment_thesis", "No investment thesis available.")
    target_price = getattr(decision, "price_target", getattr(trader_prop, "entry_price", "N/A"))
    stop_loss = getattr(trader_prop, "stop_loss", "N/A")
    sizing = getattr(trader_prop, "position_sizing", "Standard")

    print("\n" + "=" * 60)
    print(f"# TradingAgents Decision Report: {ticker}")
    print(f"**Date:** {trade_date} | **Consensus Signal:** `{rating}`")
    print("=" * 60)
    print(f"\n### 🎯 Recommended Order Specification")
    print(f"- **Action:** `{action}`")
    print(f"- **Target Price:** `{target_price}`")
    print(f"- **Stop-Loss:** `{stop_loss}`")
    print(f"- **Recommended Sizing:** `{sizing}`")

    print(f"\n### 📋 Executive Summary")
    print(summary)

    print(f"\n### 🏛️ Investment Thesis")
    print(thesis)

    if research:
        rationale = getattr(research, "rationale", "")
        if rationale:
            print(f"\n### ⚖️ Bull vs. Bear Debate Synthesis")
            print(rationale)

    print("\n" + "=" * 60)
    print("Report complete. Order proposal is ready for user verification.")


if __name__ == "__main__":
    main()
