import json
import asyncio
from datetime import datetime
from backend.agents import ocr_agent, data_agent, news_agent, technical_agent, macro_agent, report_agent


async def run_pipeline(session_id: str, image_bytes: bytes, queues: dict, model: str = None):
    queue = queues[session_id]

    async def emit(event: dict):
        if "type" not in event:
            event["type"] = "STEP_UPDATE"
            event["timestamp"] = datetime.now().isoformat()
        elif event["type"] == "REPORT_TOKEN":
            pass  # already typed
        # Ensure all values are JSON-serializable
        try:
            json.dumps(event, default=str)
        except (TypeError, ValueError):
            # Sanitize any non-serializable values
            event = json.loads(json.dumps(event, default=str))
        await queue.put(event)

    try:
        # Step 1: OCR
        holdings = await ocr_agent.run(image_bytes, emit)
        if not holdings:
            await queue.put({
                "type": "ERROR",
                "message": "No holdings could be extracted from the image.",
            })
            return

        # Step 2: Data Fetch
        enriched_holdings, total_value, total_invested = await data_agent.run(holdings, emit)

        # Step 3: News & Sentiment
        sentiment_map = await news_agent.run(enriched_holdings, emit, model=model)

        # Step 4: Technical Analysis
        technicals_map = await technical_agent.run(enriched_holdings, emit)

        # Step 5: Macro Context
        macro_data = await macro_agent.run(emit, model=model)

        # Step 6: Report Synthesis
        report = await report_agent.run(
            enriched_holdings, technicals_map, sentiment_map, macro_data, emit, model=model
        )

        # Build final payload
        portfolio_data = {
            "total_value": total_value,
            "total_invested": total_invested,
            "total_pnl_pct": round(((total_value - total_invested) / total_invested * 100) if total_invested else 0, 2),
            "holdings": [h.model_dump() for h in enriched_holdings],
        }

        # Merge technical and sentiment data into report stocks
        enriched_report = dict(report)
        for stock in enriched_report.get("stocks", []):
            ticker = stock.get("ticker", "")
            # Find the enriched holding
            for h in enriched_holdings:
                if h.yf_ticker == ticker or h.ticker == ticker.replace(".NS", "").replace(".BO", ""):
                    stock["current_price"] = h.current_price
                    stock["day_change_pct"] = h.day_change_pct
                    stock["avg_buy_price"] = h.avg_buy_price
                    stock["quantity"] = h.quantity
                    stock["pnl_pct"] = h.pnl_pct
                    stock["current_value"] = h.current_value
                    stock["portfolio_weight_pct"] = h.portfolio_weight_pct
                    # Sparkline data (last 30 days)
                    stock["sparkline"] = [d["close"] for d in h.ohlcv[-30:]]
                    break

            # Add technicals
            if ticker in technicals_map:
                t = technicals_map[ticker]
                stock["rsi"] = t["rsi"]
                stock["macd_crossover"] = t["macd"]["crossover"]
                stock["technical_signal"] = t["signal"]

            # Add news
            if ticker in sentiment_map:
                s = sentiment_map[ticker]
                stock["news_sentiment"] = s["overall"]
                stock["news_articles"] = s.get("scored_articles", s.get("articles", []))[:3]

        await queue.put({
            "type": "COMPLETE",
            "payload": {
                "report": enriched_report,
                "portfolio": portfolio_data,
                "macro": {
                    "nifty": macro_data.get("nifty", {}),
                    "sensex": macro_data.get("sensex", {}),
                    "macro_summary": macro_data.get("macro_summary", ""),
                },
            },
        })

    except Exception as e:
        await queue.put({
            "type": "ERROR",
            "message": str(e),
        })
