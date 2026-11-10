"""Financial Modeling Prep (FMP) Vendor.

Provides institutional-grade fundamentals, real-time quotes, and financial statements
via the FMP REST API (https://financialmodelingprep.com).

Requires FMP_API_KEY environment variable.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import pandas as pd
import requests

try:
    import truststore
    truststore.inject_into_ssl()
except Exception:
    pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from tradingagents.dataflows.errors import VendorNotConfiguredError, VendorError, NoMarketDataError

logger = logging.getLogger(__name__)

FMP_BASE_URL = "https://financialmodelingprep.com/stable"
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
    data = _fetch_fmp("historical-price-eod/full", {"symbol": symbol, "from": start_date, "to": end_date})
    historical = data if isinstance(data, list) else data.get("historical", [])
    if not historical:
        raise NoMarketDataError(f"No price data found for {symbol} on FMP between {start_date} and {end_date}")

    df = pd.DataFrame(historical)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        df.set_index("date", inplace=True)

    header = f"# FMP Stock Data for {symbol} from {start_date} to {end_date}\n"
    return header + df.to_csv()


def get_fmp_fundamentals(symbol: str) -> str:
    """Fetch company profile and key valuation metrics from FMP."""
    profile = _fetch_fmp("profile", {"symbol": symbol})

    res = [f"# FMP Fundamentals for {symbol}"]
    if profile and isinstance(profile, list):
        p = profile[0]
        res.append(f"Company: {p.get('companyName', p.get('name', symbol))} ({p.get('currency', 'USD')})")
        res.append(f"Sector: {p.get('sector', 'N/A')}, Industry: {p.get('industry', 'N/A')}")
        res.append(f"Price: {p.get('price')}, Market Cap: {p.get('marketCap')}")
        res.append(f"Beta: {p.get('beta')}, Range: {p.get('range', 'N/A')}")
        res.append(f"Description: {p.get('description', '')[:400]}...")

    return "\n".join(res)


def get_fmp_balance_sheet(symbol: str, limit: int = 5) -> str:
    """Fetch annual balance sheet statements from FMP."""
    data = _fetch_fmp("balance-sheet-statement", {"symbol": symbol, "limit": limit})
    if not data:
        return f"No balance sheet data found for {symbol} on FMP."
    df = pd.DataFrame(data)
    return f"# FMP Balance Sheet for {symbol}\n" + df.to_csv(index=False)


def get_fmp_cashflow(symbol: str, limit: int = 5) -> str:
    """Fetch annual cash flow statements from FMP."""
    data = _fetch_fmp("cash-flow-statement", {"symbol": symbol, "limit": limit})
    if not data:
        return f"No cash flow data found for {symbol} on FMP."
    df = pd.DataFrame(data)
    return f"# FMP Cash Flow for {symbol}\n" + df.to_csv(index=False)


def get_fmp_income_statement(symbol: str, limit: int = 5) -> str:
    """Fetch annual income statements from FMP."""
    data = _fetch_fmp("income-statement", {"symbol": symbol, "limit": limit})
    if not data:
        return f"No income statement data found for {symbol} on FMP."
    df = pd.DataFrame(data)
    return f"# FMP Income Statement for {symbol}\n" + df.to_csv(index=False)


def get_fmp_news(symbol: str, start_date: str | None = None, end_date: str | None = None) -> str:
    """Fetch news articles for symbol from FMP."""
    data = _fetch_fmp("news/articles", {"symbols": symbol, "limit": 15})
    if not data or not isinstance(data, list):
        return f"No FMP news found for {symbol}."

    res = [f"# FMP News for {symbol}:"]
    for item in data[:10]:
        res.append(f"- [{item.get('date', item.get('publishedDate'))}] {item.get('title')} ({item.get('site', 'FMP')})")
        res.append(f"  {item.get('text', '')[:200]}...")
    return "\n".join(res)
