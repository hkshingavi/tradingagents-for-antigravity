#!/usr/bin/env python3
"""Quantitative Screener for all 100 constituents of the NIFTY Midcap 100 Index.

Screens all 100 constituents based on:
1. Fundamental Quality (ROE, Margins, Debt/Equity, Earnings Growth)
2. Valuation & Upside (Forward P/E, Analyst Consensus Target Upside, Recommendation)
3. Technical Health (Price vs 50-DMA & 200-DMA, Momentum, Proximity to 52w High)
"""

import concurrent.futures
import csv
import io
import json
import os
import sys
import time
from pathlib import Path

import requests
import truststore
truststore.inject_into_ssl()

import pandas as pd
import yfinance as yf

CSV_URL = "https://www.niftyindices.com/IndexConstituent/ind_niftymidcap100list.csv"

def get_constituents():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(CSV_URL, headers=headers, timeout=15)
    r.raise_for_status()
    reader = csv.DictReader(io.StringIO(r.text))
    items = []
    for row in reader:
        sym = row.get("Symbol", "").strip()
        name = row.get("Company Name", "").strip()
        ind = row.get("Industry", "").strip()
        if sym:
            items.append({"symbol": sym, "ticker": f"{sym}.NS", "name": name, "industry": ind})
    return items

def analyze_ticker(item):
    ticker = item["ticker"]
    sym = item["symbol"]
    try:
        tk = yf.Ticker(ticker)
        info = tk.info or {}
        hist = tk.history(period="1y")
        if hist.empty or len(hist) < 50:
            return None
        
        current_price = info.get("currentPrice") or info.get("regularMarketPrice") or hist["Close"].iloc[-1]
        if not current_price or current_price <= 0:
            return None
        
        sma50 = hist["Close"].rolling(50).mean().iloc[-1]
        sma200 = hist["Close"].rolling(200).mean().iloc[-1] if len(hist) >= 200 else sma50
        w52_high = hist["High"].max()
        w52_low = hist["Low"].min()
        
        # Technical metrics
        above_50 = current_price >= sma50
        above_200 = current_price >= sma200
        dist_52w_high = ((current_price - w52_high) / w52_high) * 100
        
        # Fundamental metrics
        trailing_pe = info.get("trailingPE")
        forward_pe = info.get("forwardPE")
        peg_ratio = info.get("pegRatio")
        roe = info.get("returnOnEquity")
        if roe is not None:
            roe = roe * 100  # Percentage
        profit_margin = info.get("profitMargins")
        if profit_margin is not None:
            profit_margin = profit_margin * 100
        earnings_growth = info.get("earningsGrowth")
        if earnings_growth is not None:
            earnings_growth = earnings_growth * 100
        debt_to_equity = info.get("debtToEquity")
        target_mean_price = info.get("targetMeanPrice")
        recommendation = info.get("recommendationKey", "none")
        
        upside_pct = 0.0
        if target_mean_price and current_price:
            upside_pct = ((target_mean_price - current_price) / current_price) * 100
            
        # Scoring logic
        score = 0.0
        
        # 1. Technical Score (max 30 pts)
        if above_200:
            score += 15
        if above_50:
            score += 10
        if -20 <= dist_52w_high <= 0: # Consolidating near highs
            score += 5
            
        # 2. Fundamental Quality Score (max 40 pts)
        if roe is not None:
            if roe > 20:
                score += 15
            elif roe > 14:
                score += 10
            elif roe > 8:
                score += 5
                
        if profit_margin is not None:
            if profit_margin > 15:
                score += 10
            elif profit_margin > 8:
                score += 5
                
        if earnings_growth is not None and earnings_growth > 0:
            score += 5
            if earnings_growth > 15:
                score += 5
                
        # Debt prudence (exclude financials where debt is working capital)
        is_financial = "financial" in item["industry"].lower() or "bank" in item["industry"].lower()
        if not is_financial:
            if debt_to_equity is not None:
                if debt_to_equity < 50:
                    score += 5
                elif debt_to_equity > 180:
                    score -= 5
                    
        # 3. Valuation & Upside Score (max 30 pts)
        if recommendation in ("buy", "strong_buy"):
            score += 15
        elif recommendation == "hold":
            score += 5
            
        if upside_pct > 20:
            score += 15
        elif upside_pct > 10:
            score += 10
        elif upside_pct > 0:
            score += 5
            
        return {
            "symbol": sym,
            "ticker": ticker,
            "name": item["name"],
            "industry": item["industry"],
            "price": round(current_price, 2),
            "target": round(target_mean_price, 2) if target_mean_price else None,
            "upside_pct": round(upside_pct, 1),
            "recommendation": recommendation,
            "roe": round(roe, 1) if roe is not None else None,
            "trailing_pe": round(trailing_pe, 1) if trailing_pe else None,
            "forward_pe": round(forward_pe, 1) if forward_pe else None,
            "debt_to_equity": round(debt_to_equity, 1) if debt_to_equity else None,
            "above_50": above_50,
            "above_200": above_200,
            "score": round(score, 1),
        }
    except Exception as e:
        return None

def main():
    print("[*] Fetching Nifty Midcap 100 constituent list from NSE...")
    constituents = get_constituents()
    print(f"[*] Found {len(constituents)} constituents. Running parallel quantitative analysis...")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_item = {executor.submit(analyze_ticker, item): item for item in constituents}
        completed = 0
        for future in concurrent.futures.as_completed(future_to_item):
            completed += 1
            if completed % 20 == 0 or completed == len(constituents):
                print(f"[*] Processed {completed}/{len(constituents)} stocks...")
            res = future.result()
            if res:
                results.append(res)
                
    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"\n[+] Successfully analyzed {len(results)} stocks.")
    print("\n" + "=" * 90)
    print(f"{'Rank':<5}{'Symbol':<12}{'Industry':<22}{'CMP (₹)':<10}{'Target':<10}{'Upside%':<10}{'ROE%':<8}{'Rec':<12}{'Score'}")
    print("=" * 90)
    
    for i, r in enumerate(results[:20], 1):
        target_str = f"₹{r['target']}" if r['target'] else "N/A"
        roe_str = f"{r['roe']}%" if r['roe'] is not None else "N/A"
        print(f"{i:<5}{r['symbol']:<12}{r['industry'][:20]:<22}{r['price']:<10}{target_str:<10}{r['upside_pct']:<10}{roe_str:<8}{r['recommendation']:<12}{r['score']}")
        
    # Save results to json
    out_path = Path("midcap100_screen_results.json")
    out_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"\n[+] Full dataset saved to {out_path.resolve()}")

if __name__ == "__main__":
    main()
