import time
from backend.tools.calculations import compute_rsi, compute_macd, compute_sma, compute_bollinger, determine_signal


async def run(enriched_holdings, emit):
    start = time.time()
    tickers_str = ", ".join([h.yf_ticker for h in enriched_holdings])

    await emit({
        "step_id": "technical_agent",
        "step_name": "Technical Analysis",
        "status": "running",
        "icon": "📈",
        "input_summary": f"Computing indicators for {tickers_str}",
        "output_summary": "",
        "details": ["Starting technical analysis..."],
        "data": None,
        "duration_ms": 0,
    })

    technicals_map = {}
    details = ["Starting technical analysis..."]

    for holding in enriched_holdings:
        ticker = holding.yf_ticker
        ohlcv = holding.ohlcv

        if not ohlcv or len(ohlcv) < 5:
            technicals_map[ticker] = {
                "rsi": 50.0,
                "macd": {"macd": 0, "signal": 0, "histogram": 0, "crossover": "NONE"},
                "sma20": 0,
                "sma50": 0,
                "bollinger": {"upper": 0, "middle": 0, "lower": 0, "position": "MIDDLE"},
                "signal": "HOLD",
                "golden_cross": False,
                "death_cross": False,
            }
            details.append(f"⚠ {ticker}: Insufficient data, defaulting to HOLD")
            continue

        closes = [d["close"] for d in ohlcv]

        rsi = compute_rsi(closes)
        macd = compute_macd(closes)
        sma20 = compute_sma(closes, 20)
        sma50 = compute_sma(closes, 50)
        bollinger = compute_bollinger(closes)

        # Golden/Death cross detection
        golden_cross = False
        death_cross = False
        if len(sma20) >= 2 and len(sma50) >= 2 and sma20[-1] > 0 and sma50[-1] > 0:
            if sma20[-1] > sma50[-1] and sma20[-2] <= sma50[-2]:
                golden_cross = True
            elif sma20[-1] < sma50[-1] and sma20[-2] >= sma50[-2]:
                death_cross = True

        signal = determine_signal(rsi, macd, sma20, sma50, bollinger)

        technicals_map[ticker] = {
            "rsi": rsi,
            "macd": macd,
            "sma20": round(sma20[-1], 2) if sma20 else 0,
            "sma50": round(sma50[-1], 2) if sma50 else 0,
            "bollinger": bollinger,
            "signal": signal,
            "golden_cross": golden_cross,
            "death_cross": death_cross,
        }

        rsi_label = "Overbought" if rsi > 70 else ("Oversold" if rsi < 30 else "Neutral")
        details.append(f"✓ {ticker}: {signal} | RSI: {rsi} ({rsi_label}) | MACD: {macd['crossover']}")

        await emit({
            "step_id": "technical_agent",
            "step_name": "Technical Analysis",
            "status": "running",
            "icon": "📈",
            "input_summary": f"Computing indicators for {tickers_str}",
            "output_summary": "",
            "details": list(details),
            "data": None,
            "duration_ms": int((time.time() - start) * 1000),
        })

    signals_summary = ", ".join([f"{k.split('.')[0]}={v['signal']}" for k, v in technicals_map.items()])
    duration = int((time.time() - start) * 1000)

    await emit({
        "step_id": "technical_agent",
        "step_name": "Technical Analysis",
        "status": "done",
        "icon": "📈",
        "input_summary": f"Analyzed {len(enriched_holdings)} stocks",
        "output_summary": signals_summary,
        "details": details,
        "data": {"technicals": {k: v["signal"] for k, v in technicals_map.items()}},
        "duration_ms": duration,
    })

    return technicals_map
