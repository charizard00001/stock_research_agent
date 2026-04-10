import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from backend.models.portfolio import Holding, EnrichedHolding
from backend.tools.stock_data import get_stock_info, get_ohlcv

executor = ThreadPoolExecutor(max_workers=2)


async def run(holdings: list[Holding], emit):
    start = time.time()
    tickers_str = ", ".join([h.ticker for h in holdings])

    await emit({
        "step_id": "data_agent",
        "step_name": "Market Data Fetch",
        "status": "running",
        "icon": "📊",
        "input_summary": f"Fetching data for {tickers_str}",
        "output_summary": "",
        "details": [f"Starting data fetch for {len(holdings)} stocks..."],
        "data": None,
        "duration_ms": 0,
    })

    enriched = []
    details = [f"Starting data fetch for {len(holdings)} stocks..."]

    loop = asyncio.get_event_loop()

    for h in holdings:
        yf_ticker = h.yf_ticker
        details.append(f"Fetching {yf_ticker}...")

        await emit({
            "step_id": "data_agent",
            "step_name": "Market Data Fetch",
            "status": "running",
            "icon": "📊",
            "input_summary": f"Fetching data for {tickers_str}",
            "output_summary": "",
            "details": list(details),
            "data": None,
            "duration_ms": int((time.time() - start) * 1000),
        })

        info = await loop.run_in_executor(executor, get_stock_info, yf_ticker)
        await asyncio.sleep(1)  # Rate limit protection
        ohlcv = await loop.run_in_executor(executor, get_ohlcv, yf_ticker)
        await asyncio.sleep(1)  # Rate limit protection

        current_value = info["current_price"] * h.quantity
        invested = h.avg_buy_price * h.quantity
        pnl_pct = ((current_value - invested) / invested * 100) if invested else 0

        eh = EnrichedHolding(
            ticker=h.ticker,
            yf_ticker=yf_ticker,
            company_name=info.get("company_name", h.ticker),
            quantity=h.quantity,
            avg_buy_price=h.avg_buy_price,
            exchange=h.exchange,
            current_price=info["current_price"],
            day_change_pct=info["day_change_pct"],
            high_52w=info["high_52w"],
            low_52w=info["low_52w"],
            pe_ratio=info.get("pe_ratio"),
            eps=info.get("eps"),
            market_cap=info.get("market_cap"),
            beta=info.get("beta"),
            current_value=round(current_value, 2),
            pnl_pct=round(pnl_pct, 2),
            ohlcv=ohlcv,
        )
        enriched.append(eh)

        details[-1] = f"✓ {yf_ticker} — ₹{info['current_price']} ({info['day_change_pct']:+.2f}%)"

        await emit({
            "step_id": "data_agent",
            "step_name": "Market Data Fetch",
            "status": "running",
            "icon": "📊",
            "input_summary": f"Fetching data for {tickers_str}",
            "output_summary": "",
            "details": list(details),
            "data": None,
            "duration_ms": int((time.time() - start) * 1000),
        })

    # Compute portfolio weights
    total_value = sum(e.current_value for e in enriched)
    for e in enriched:
        e.portfolio_weight_pct = round((e.current_value / total_value * 100) if total_value else 0, 2)

    total_invested = sum(e.quantity * e.avg_buy_price for e in enriched)
    total_pnl = ((total_value - total_invested) / total_invested * 100) if total_invested else 0

    summary = f"Total value: ₹{total_value:,.2f} | P&L: {total_pnl:+.2f}%"
    details.append(f"✓ Portfolio total: ₹{total_value:,.2f}")

    duration = int((time.time() - start) * 1000)
    await emit({
        "step_id": "data_agent",
        "step_name": "Market Data Fetch",
        "status": "done",
        "icon": "📊",
        "input_summary": f"Fetched data for {len(holdings)} stocks",
        "output_summary": summary,
        "details": details,
        "data": {
            "total_value": total_value,
            "total_invested": total_invested,
            "total_pnl_pct": round(total_pnl, 2),
        },
        "duration_ms": duration,
    })

    return enriched, total_value, total_invested
