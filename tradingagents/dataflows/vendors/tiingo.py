"""Tiingo Market & News Vendor.

Provides high-cleanliness historical end-of-day data and curated news feeds
with exact ticker tagging via Tiingo REST API (https://api.tiingo.com).

Requires TIINGO_API_KEY environment variable.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import pandas as pd
import requests

from tradingagents.dataflows.errors import VendorNotConfiguredError, VendorError, NoMarketDataError

logger = logging.getLogger(__name__)

TIINGO_BASE_URL = "https://api.tiingo.com/tiingo"
REQUEST_TIMEOUT = 30


def _get_api_key() -> str:
    key = os.environ.get("TIINGO_API_KEY")
    if not key:
        raise VendorNotConfiguredError("Tiingo", "TIINGO_API_KEY")
    return key


def _get_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Authorization": f"Token {_get_api_key()}",
    }


def get_tiingo_stock(symbol: str, start_date: str, end_date: str) -> str:
    """Fetch daily adjusted prices from Tiingo."""
    url = f"{TIINGO_BASE_URL}/daily/{symbol}/prices"
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "format": "json",
    }
    try:
        response = requests.get(url, headers=_get_headers(), params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise NoMarketDataError(f"No price data found for {symbol} on Tiingo between {start_date} and {end_date}")

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        header = f"# Tiingo Stock Data for {symbol} from {start_date} to {end_date}\n"
        return header + df.to_csv()
    except requests.exceptions.RequestException as e:
        raise VendorError(f"Tiingo API request failed: {e}") from e


def get_tiingo_news(symbol: str, start_date: str | None = None, end_date: str | None = None) -> str:
    """Fetch ticker-tagged news articles from Tiingo News feed."""
    url = f"{TIINGO_BASE_URL}/news"
    params: dict[str, Any] = {"tickers": symbol, "limit": 20}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    try:
        response = requests.get(url, headers=_get_headers(), params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        articles = response.json()
        if not articles:
            return f"No Tiingo news found for {symbol}."

        res = [f"# Tiingo News for {symbol}:"]
        for a in articles[:15]:
            pub_date = a.get("publishedDate", "")[:10]
            res.append(f"- [{pub_date}] {a.get('title')} ({a.get('source')})")
            res.append(f"  {a.get('description', '')[:200]}...")
        return "\n".join(res)
    except requests.exceptions.RequestException as e:
        raise VendorError(f"Tiingo News request failed: {e}") from e
