import numpy as np
import pandas as pd


def compute_sma(closes: list[float], window: int) -> list[float]:
    s = pd.Series(closes)
    return s.rolling(window=window).mean().fillna(0).tolist()


def compute_rsi(closes: list[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0
    s = pd.Series(closes)
    delta = s.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean().iloc[-1]
    avg_loss = loss.rolling(window=period).mean().iloc[-1]
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def compute_macd(closes: list[float]) -> dict:
    if len(closes) < 26:
        return {"macd": 0, "signal": 0, "histogram": 0, "crossover": "NONE"}
    s = pd.Series(closes)
    ema12 = s.ewm(span=12, adjust=False).mean()
    ema26 = s.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    crossover = "NONE"
    if len(histogram) >= 2:
        if histogram.iloc[-1] > 0 and histogram.iloc[-2] <= 0:
            crossover = "BULLISH"
        elif histogram.iloc[-1] < 0 and histogram.iloc[-2] >= 0:
            crossover = "BEARISH"

    return {
        "macd": round(macd_line.iloc[-1], 4),
        "signal": round(signal_line.iloc[-1], 4),
        "histogram": round(histogram.iloc[-1], 4),
        "crossover": crossover,
    }


def compute_bollinger(closes: list[float], window: int = 20) -> dict:
    if len(closes) < window:
        return {"upper": 0, "middle": 0, "lower": 0, "position": "MIDDLE"}
    s = pd.Series(closes)
    middle = s.rolling(window=window).mean()
    std = s.rolling(window=window).std()
    upper = middle + 2 * std
    lower = middle - 2 * std

    current = closes[-1]
    pos = "MIDDLE"
    if current >= upper.iloc[-1]:
        pos = "ABOVE_UPPER"
    elif current <= lower.iloc[-1]:
        pos = "BELOW_LOWER"

    return {
        "upper": round(upper.iloc[-1], 2),
        "middle": round(middle.iloc[-1], 2),
        "lower": round(lower.iloc[-1], 2),
        "position": pos,
    }


def determine_signal(rsi: float, macd: dict, sma20: list, sma50: list, bollinger: dict) -> str:
    score = 0

    # RSI
    if rsi < 30:
        score += 2
    elif rsi < 40:
        score += 1
    elif rsi > 70:
        score -= 2
    elif rsi > 60:
        score -= 1

    # MACD
    if macd["crossover"] == "BULLISH":
        score += 2
    elif macd["crossover"] == "BEARISH":
        score -= 2
    elif macd["histogram"] > 0:
        score += 1
    else:
        score -= 1

    # SMA crossover
    if sma20 and sma50 and sma20[-1] > 0 and sma50[-1] > 0:
        if sma20[-1] > sma50[-1]:
            score += 1
        else:
            score -= 1

    # Bollinger
    if bollinger["position"] == "BELOW_LOWER":
        score += 1
    elif bollinger["position"] == "ABOVE_UPPER":
        score -= 1

    if score >= 4:
        return "STRONG BUY"
    elif score >= 2:
        return "BUY"
    elif score <= -4:
        return "STRONG SELL"
    elif score <= -2:
        return "SELL"
    return "HOLD"


def compute_portfolio_metrics(holdings_data: list[dict]) -> dict:
    total_value = sum(h.get("current_value", 0) for h in holdings_data)
    total_invested = sum(h.get("quantity", 0) * h.get("avg_buy_price", 0) for h in holdings_data)
    overall_pnl = ((total_value - total_invested) / total_invested * 100) if total_invested else 0
    return {
        "total_value": round(total_value, 2),
        "total_invested": round(total_invested, 2),
        "overall_pnl_pct": round(overall_pnl, 2),
    }
