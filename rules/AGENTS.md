# TradingAgents for Antigravity — Rules & Operational Guidelines

This plugin provides the multi-agent LLM financial trading framework adapted for Google Antigravity.

## Architectural Principles

1. **Dual-Tier Model Routing (Cost & Speed Optimization):**
   * **Quick-Think Tier (`quick_think_llm`):** Runs the 4 parallel data-heavy analysts (Market/Technicals, Fundamentals, News, Social Sentiment). Defaults to `gemini-2.5-flash` (or local Ollama `qwen2.5:8b`).
   * **Deep-Think Tier (`deep_think_llm`):** Runs the Bull vs. Bear adversarial debate, Risk Management team, and the Portfolio Manager. Defaults to `gemini-2.5-pro` with thinking/reasoning enabled (or local `deepseek-r1:14b/32b`).
   * This separation minimizes cloud token costs while maximizing reasoning depth where it matters most.

2. **Global & Multi-Asset Support:**
   * Tickers are automatically normalized:
     * US Equities: `NVDA`, `AAPL`, `SPY`
     * Global Equities: `RELIANCE.NS`, `TCS.NS`, `0700.HK`, `SAP.DE`
     * Cryptocurrencies: `BTC-USD`, `ETH-USD`
     * Forex: `EURUSD`, `USDINR`
     * Commodities: `GC=F` (Gold), `CL=F` (Crude Oil)

3. **Safety & Broker Execution:**
   * **Advisory & Simulation by Default:** No trade is placed without user confirmation.
   * **Order Execution Handoff:** When the user decides to act on an approved trade proposal, format the order for the `trader-broker` skill (Alpaca MCP server or supported broker) and require explicit user approval in chat.

4. **Environment Variables:**
   * `GOOGLE_API_KEY`: Required when using Google Gemini tiers.
   * `OLLAMA_BASE_URL`: (Optional) Defaults to `http://localhost:11434/v1` when offloading the analyst tier to local models.
   * `SEC_USER_AGENT`: User contact string (e.g. `Name user@example.com`) for point-in-time SEC EDGAR filings.
