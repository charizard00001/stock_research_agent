import yfinance as yf
import pandas as pd
import time


def _retry_history(ticker_obj, period="5d", max_retries=3):
    """Fetch history with retry on rate limit."""
    for attempt in range(max_retries):
        hist = ticker_obj.history(period=period)
        if not hist.empty:
            return hist
        if attempt < max_retries - 1:
            time.sleep(2 * (attempt + 1))
    return pd.DataFrame()


def _safe_info(ticker_obj) -> dict:
    """Fetch .info with fallback on rate limit / errors."""
    try:
        return ticker_obj.info
    except Exception:
        return {}


def get_stock_info(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)

        # Try .info first for live current price
        info = _safe_info(stock)

        # History for prev close and fallback price
        hist = _retry_history(stock, period="5d")
        hist = hist.dropna(subset=["Close"])  # Drop incomplete rows

        # Prefer live price from .info, fall back to last history close
        live_price = info.get("currentPrice") or info.get("regularMarketPrice")
        hist_close = round(float(hist["Close"].iloc[-1]), 2) if not hist.empty else None

        current_price = live_price or hist_close or 0

        # Previous close: from .info or second-to-last history row
        prev_close = info.get("previousClose")
        if not prev_close and not hist.empty and len(hist) > 1:
            prev_close = float(hist["Close"].iloc[-2])
        if not prev_close:
            prev_close = current_price

        day_change = ((current_price - prev_close) / prev_close * 100) if prev_close else 0

        return {
            "current_price": round(current_price, 2),
            "day_change_pct": round(day_change, 2),
            "high_52w": info.get("fiftyTwoWeekHigh", 0),
            "low_52w": info.get("fiftyTwoWeekLow", 0),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "market_cap": info.get("marketCap"),
            "beta": info.get("beta"),
            "company_name": info.get("shortName", ticker),
        }
    except Exception as e:
        return {
            "current_price": 0,
            "day_change_pct": 0,
            "high_52w": 0,
            "low_52w": 0,
            "pe_ratio": None,
            "eps": None,
            "market_cap": None,
            "beta": None,
            "company_name": ticker,
            "error": str(e),
        }


def get_ohlcv(ticker: str, period: str = "6mo") -> list[dict]:
    try:
        stock = yf.Ticker(ticker)
        hist = _retry_history(stock, period=period)
        if hist.empty:
            return []
        hist = hist.dropna(subset=["Close"])
        records = []
        for date, row in hist.iterrows():
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"]),
            })
        return records
    except Exception:
        return []


def get_index_data(symbol: str = "^NSEI") -> dict:
    try:
        idx = yf.Ticker(symbol)
        hist = idx.history(period="5d")
        if hist.empty:
            return {"price": 0, "change_pct": 0}
        current = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2] if len(hist) > 1 else current
        change = ((current - prev) / prev * 100) if prev else 0
        return {
            "price": round(current, 2),
            "change_pct": round(change, 2),
            "name": symbol,
        }
    except Exception:
        return {"price": 0, "change_pct": 0, "name": symbol}
