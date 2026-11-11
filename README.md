# TradingAgents for Antigravity

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

An adaptation of the **[TradingAgents](https://github.com/TauricResearch/TradingAgents)** multi-agent LLM financial trading framework designed specifically for **Google Antigravity**.

Emulates an institutional hedge fund research desk with **5 collaborative agent teams** (Fundamentals, Technicals, News, Sentiment, Bull/Bear Researchers, Risk Managers, and Portfolio Manager).

---

## 🚀 Key Highlights & Enhancements

* **Dual-Tier Model Routing (Cost & Speed Optimized):**
  * **Quick-Think Tier (`gemini-2.5-flash`):** High-speed parallel market data crunching, balance sheet parsing, and indicator generation.
  * **Deep-Think Tier (`gemini-2.5-pro`):** Deep chain-of-thought Bull vs. Bear debate, risk review, and portfolio sizing.
  * **Local Ollama Offload:** Option to run the analyst tier 100% locally on your machine (`qwen2.5:8b`), cutting cloud API consumption by ~75%.
* **Multi-Asset & Global Markets:**
  * US Equities (`NVDA`, `AAPL`, `SPY`) with point-in-time SEC EDGAR filings.
  * Indian Markets (`RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`).
  * Global Equities (Hong Kong, Europe, Japan).
  * Cryptocurrencies (`BTC-USD`, `ETH-USD`) & Forex (`EURUSD`, `USDINR`).
* **Antigravity Skills:**
  * Run analyses directly via Antigravity chat: `/tradingagents-analyze <TICKER>`.
  * Inspect generated reports with `/tradingagents-report`.
* **Broker-Ready Execution:**
  * Directly pairs with Antigravity broker skills (such as `trader-broker` / Alpaca MCP) to execute approved trades with explicit user confirmation.
* **Full-Index Quantitative Screener:**
  * Automated screening engine (`screen_midcap100.py`) evaluating entire index universes (e.g. Nifty Midcap 100) across ROE, P/E multiples, debt-to-equity, 50/200 DMA trend checks, and institutional target upsides.
* **Institutional Excel & PowerPoint Reporting:**
  * One-click generation of polished `.xlsx` financial workbooks and `.pptx` executive presentation decks with independent valuation audits.
* **Independent Fair Value Valuation Engine:**
  * Multi-factor forward EPS valuation models that independently calculate target prices and stress-test them against broker consensus.

---

## 🏛️ The 5-Team Architecture

```
[ Market Data & Catalysts ]
           │
           ▼
┌────────────────────────────────────────────────────────┐
│ 1. THE ANALYST TEAM (Parallel Analysis)                │
│  • Fundamentals   • Technical   • News   • Sentiment   │
│  ───► Powered by Quick-Think Tier (Gemini Flash / Ollama)
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. RESEARCH TEAM (Adversarial Debate)                  │
│  • Bull Researcher ◄──── Debate ────► Bear Researcher  │
│  ───► Powered by Deep-Think Tier (Gemini Pro Thinking) │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. TRADER AGENT                                        │
│  • Formulates strategy: BUY / SELL / HOLD              │
│  • Sets entry price, target price, and time horizon    │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 4. RISK MANAGEMENT TEAM (3-Perspective Debate)         │
│  • Aggressive Debater • Neutral • Conservative Debater │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 5. PORTFOLIO MANAGER (Final Decision / CIO)            │
│  • Approves, rejects, or adjusts order sizing & stops  │
│  • Generates execution report                          │
└──────────────────────────┬─────────────────────────────┘
```

---

## 📦 Installation in Google Antigravity

### 1. Clone into your Antigravity Plugins Directory

```powershell
# Windows
git clone https://github.com/hkshingavi/tradingagents-for-antigravity.git "$env:USERPROFILE\.gemini\config\plugins\tradingagents-for-antigravity"
```

```bash
# macOS / Linux
git clone https://github.com/hkshingavi/tradingagents-for-antigravity.git ~/.gemini/config/plugins/tradingagents-for-antigravity
```

### 2. Set Up Python Dependencies

Navigate to the plugin directory and run the automated setup script:

```powershell
# Windows (PowerShell)
cd "$env:USERPROFILE\.gemini\config\plugins\tradingagents-for-antigravity"
.\setup.ps1
```

```bash
# macOS / Linux
cd ~/.gemini/config/plugins/tradingagents-for-antigravity
chmod +x setup.sh && ./setup.sh
```

### 3. Configure API Keys

Copy the example environment file and add your Google AI Studio API key:

```powershell
cp .env.example .env
```

Edit `.env`:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## 💡 Usage Examples

Run directly from Antigravity or terminal:

```bash
# Analyze any US stock on the latest completed trading day
python run_adapter.py --ticker NVDA

# Analyze Indian equities (NSE)
python run_adapter.py --ticker RELIANCE.NS

# Offload data analysts to local Ollama (saving 75% API quota)
python run_adapter.py --ticker TSLA --quick-provider ollama --quick-llm qwen2.5:8b

# Historical point-in-time backtesting
python run_adapter.py --ticker AAPL --date 2026-09-01

# Run the full 100-constituent quantitative index screener
python screen_midcap100.py

# Generate institutional Excel (.xlsx) and PowerPoint (.pptx) reports
python generate_reports.py
```

---

## 🛡️ Disclaimer

This framework is built for research, educational, and simulation purposes. It does not provide financial or investment advice. Always perform your own due diligence before risking real capital.

---

## 📄 License & Attribution

* Framework adapted from the original open-source [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents).
* Distributed under the Apache 2.0 License.
