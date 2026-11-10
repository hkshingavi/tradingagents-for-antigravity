"""OpenBB Platform Vendor.

Connects to the OpenBB Platform (https://openbb.co) to aggregate data across
institutional providers (FMP, Polygon, Tiingo, Intrinio, SEC, Federal Reserve).

Requires the OpenBB Platform SDK installed (`pip install openbb`) or configured
via OPENBB_PAT (Personal Access Token).
"""

from __future__ import annotations

import logging
import os
from typing import Any

from tradingagents.dataflows.errors import VendorNotConfiguredError, VendorError, NoMarketDataError

logger = logging.getLogger(__name__)


def _check_openbb():
    try:
        from openbb import obb
        return obb
    except ImportError:
        raise VendorNotConfiguredError(
            "OpenBB",
            "OpenBB SDK not installed. Run: pip install openbb or configure OPENBB_PAT"
        )


def get_openbb_stock(symbol: str, start_date: str, end_date: str, provider: str = "fmp") -> str:
    """Fetch historical daily price data using OpenBB."""
    obb = _check_openbb()
    pat = os.environ.get("OPENBB_PAT")
    if pat:
        obb.account.login(pat=pat)

    try:
        res = obb.equity.price.historical(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            provider=provider
        )
        df = res.to_df()
        if df.empty:
            raise NoMarketDataError(f"No OpenBB data returned for {symbol} ({provider})")
        header = f"# OpenBB ({provider}) Stock Data for {symbol} from {start_date} to {end_date}\n"
        return header + df.to_csv()
    except Exception as e:
        raise VendorError(f"OpenBB historical fetch failed: {e}") from e


def get_openbb_fundamentals(symbol: str, provider: str = "fmp") -> str:
    """Fetch company profile and fundamentals using OpenBB."""
    obb = _check_openbb()
    try:
        profile = obb.equity.fundamental.profile(symbol=symbol, provider=provider).to_df()
        metrics = obb.equity.fundamental.metrics(symbol=symbol, provider=provider).to_df()
        res = [f"# OpenBB Fundamentals for {symbol} ({provider})", "\n## Profile:"]
        res.append(profile.to_string())
        res.append("\n## Metrics:")
        res.append(metrics.to_string())
        return "\n".join(res)
    except Exception as e:
        raise VendorError(f"OpenBB fundamentals fetch failed: {e}") from e
