"""Financial Modeling Prep (FMP) Vendor.

Provides institutional-grade fundamentals, real-time & historical OHLCV data,
and financial statements via the FMP REST API (https://financialmodelingprep.com).

Requires FMP_API_KEY environment variable.
"""

from __future__ import annotations

import io
import logging
import os
from datetime import datetime
from typing import Any

import pandas as pd
import requests

from tradingagents.dataflows.errors import VendorNotConfiguredError, VendorError, NoMarketDataError

logger = logging.getLogger(__name__)

FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
REQUEST_TIMEOUT = 30


def _get_api_key() -> str:
    key = os.environ.get("FMP_API_KEY") or os.environ.get("FINANCIAL_MODELING_PREP_API_KEY")
    if not key:
        raise VendorNotConfiguredError("FMP", "FMP_API_KEY")
    return key


def _fetch_fmp(endpoint: str, params: dict[str, Any] | None = None) -> Any:
    key = _get_api_key()
    url = f"{FMP_BASE_URL}/{endpoint}"
    req_params = params.copy() if params else {}
    req_params["apikey"] = key

    try:
        response = requests.get(url, params=req_params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "Error Message" in data:
            raise VendorError(f"FMP API Error: {data['Error Message']}")
        return data
    except requests.exceptions.RequestException as e:
        raise VendorError(f"FMP Request failed: {e}") from e


def get_fmp_stock(symbol: str, start_date: str, end_date: str) -> str:
    """Fetch historical daily price data from FMP."""
    data = _fetch_fmp(f"historical-price-full/{symbol}", {"from": start_date, "to": end_date})
    historical = data.get("historical", [])
    if not historical:
        raise NoMarketDataError(f"No price data found for {symbol} on FMP between {start_date} and {end_date}")

    df = pd.DataFrame(historical)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df.set_index("date", inplace=True)

    header = f"# FMP Stock Data for {symbol} from {start_date} to {end_date}\n"
    return header + df.to_csv()


def get_fmp_fundamentals(symbol: str) -> str:
    """Fetch company profile and key valuation metrics from FMP."""
    profile = _fetch_fmp(f"profile/{symbol}")
    metrics = _fetch_fmp(f"key-metrics-ttm/{symbol}")

    res = [f"# FMP Fundamentals for {symbol}"]
    if profile and isinstance(profile, list):
        p = profile[0]
        res.append(f"Company: {p.get('companyName')} ({p.get('currency', 'USD')})")
        res.append(f"Sector: {p.get('sector')}, Industry: {p.get('industry')}")
        res.append(f"Price: {p.get('price')}, Market Cap: {p.get('mktCap')}")
        res.append(f"Beta: {p.get('beta')}, Range: {p.get('range')}")
        res.append(f"Description: {p.get('description', '')[:400]}...")

    if metrics and isinstance(metrics, list):
        m = metrics[0]
        res.append("\n## Key TTM Metrics:")
        for k in ["peRatioTTM", "priceToSalesRatioTTM", "pbRatioTTM", "enterpriseValueOverEBITDATTM", "netDebtToEBITDATTM", "roeTTM"]:
            if k in m:
                res.append(f"- {k}: {m[k]}")

    return "\n".join(res)


def get_fmp_balance_sheet(symbol: str, limit: int = 5) -> str:
    """Fetch annual balance sheet statements from FMP."""
    data = _fetch_fmp(f"balance-sheet-statement/{symbol}", {"limit": limit})
    if not data:
        return f"No balance sheet data found for {symbol} on FMP."
    df = pd.DataFrame(data)
    return f"# FMP Balance Sheet for {symbol}\n" + df.to_csv(index=False)


def get_fmp_cashflow(symbol: str, limit: int = 5) -> str:
    """Fetch annual cash flow statements from FMP."""
    data = _fetch_fmp(f"cash-flow-statement/{symbol}", {"limit": limit})
    if not data:
        return f"No cash flow data found for {symbol} on FMP."
    df = pd.DataFrame(data)
    return f"# FMP Cash Flow for {symbol}\n" + df.to_csv(index=False)


def get_fmp_income_statement(symbol: str, limit: int = 5) -> str:
    """Fetch annual income statements from FMP."""
    data = _fetch_fmp(f"income-statement/{symbol}", {"limit": limit})
    if not data:
        return f"No income statement data found for {symbol} on FMP."
    df = pd.DataFrame(data)
    return f"# FMP Income Statement for {symbol}\n" + df.to_csv(index=False)


def get_fmp_news(symbol: str, start_date: str | None = None, end_date: str | None = None) -> str:
    """Fetch news articles for symbol from FMP."""
    data = _fetch_fmp("stock_news", {"tickers": symbol, "limit": 20})
    if not data:
        return f"No FMP news found for {symbol}."

    res = [f"# FMP News for {symbol}:"]
    for item in data[:15]:
        res.append(f"- [{item.get('publishedDate')}] {item.get('title')} ({item.get('site')})")
        res.append(f"  {item.get('text', '')[:200]}...")
    return "\n".join(res)
