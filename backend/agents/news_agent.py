import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from backend.llm_client import chat
from backend.tools.news_fetcher import fetch_news

executor = ThreadPoolExecutor(max_workers=5)

SENTIMENT_PROMPT = """Analyze these news headlines for {ticker} stock.
For each headline, assign:
- sentiment: BULLISH, BEARISH, or NEUTRAL
- impact_score: 1-10
- brief_reason: one sentence

Return ONLY valid JSON array, no markdown:
[{{"headline": "...", "sentiment": "BULLISH", "impact_score": 7, "brief_reason": "..."}}]

Headlines:
{headlines}"""


async def run(enriched_holdings, emit, model=None):
    start = time.time()
    tickers = [h.yf_ticker for h in enriched_holdings]
    tickers_str = ", ".join(tickers)

    await emit({
        "step_id": "news_agent",
        "step_name": "News & Sentiment",
        "status": "running",
        "icon": "📰",
        "input_summary": f"Fetching news for {tickers_str}",
        "output_summary": "",
        "details": [f"Starting news search for {len(tickers)} stocks..."],
        "data": None,
        "duration_ms": 0,
    })

    sentiment_map = {}
    details = [f"Starting news search for {len(tickers)} stocks..."]
    loop = asyncio.get_event_loop()

    for holding in enriched_holdings:
        ticker = holding.yf_ticker
        details.append(f"Querying news for {ticker}...")

        await emit({
            "step_id": "news_agent",
            "step_name": "News & Sentiment",
            "status": "running",
            "icon": "📰",
            "input_summary": f"Fetching news for {tickers_str}",
            "output_summary": "",
            "details": list(details),
            "data": None,
            "duration_ms": int((time.time() - start) * 1000),
        })

        articles = await loop.run_in_executor(executor, fetch_news, ticker)
        details[-1] = f"✓ Found {len(articles)} articles for {ticker}"

        if articles and articles[0].get("title") and not articles[0]["title"].startswith("Error"):
            headlines_text = "\n".join([f"- {a['title']}" for a in articles])
            prompt = SENTIMENT_PROMPT.format(ticker=ticker, headlines=headlines_text)

            try:
                response = chat(
                    messages=[{"role": "user", "content": prompt}],
                    system="You are a financial sentiment analyst. Return only valid JSON.",
                    model=model,
                )
                raw = response.choices[0].message.content.strip()
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0]
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0]

                scored = json.loads(raw.strip())
                bullish = sum(1 for s in scored if s.get("sentiment") == "BULLISH")
                bearish = sum(1 for s in scored if s.get("sentiment") == "BEARISH")
                total = len(scored) if scored else 1
                bullish_pct = int(bullish / total * 100)

                sentiment_map[ticker] = {
                    "articles": articles,
                    "scored_articles": scored,
                    "bullish_pct": bullish_pct,
                    "overall": "BULLISH" if bullish_pct >= 60 else ("BEARISH" if bullish_pct <= 30 else "NEUTRAL"),
                }
                details.append(f"  Sentiment for {ticker}: {sentiment_map[ticker]['overall']} ({bullish_pct}% bullish)")
            except Exception:
                sentiment_map[ticker] = {
                    "articles": articles,
                    "scored_articles": [],
                    "bullish_pct": 50,
                    "overall": "NEUTRAL",
                }
                details.append(f"  Sentiment for {ticker}: NEUTRAL (parse error)")
        else:
            sentiment_map[ticker] = {
                "articles": [],
                "scored_articles": [],
                "bullish_pct": 50,
                "overall": "NEUTRAL",
            }
            details.append(f"  No news found for {ticker}")

        await emit({
            "step_id": "news_agent",
            "step_name": "News & Sentiment",
            "status": "running",
            "icon": "📰",
            "input_summary": f"Fetching news for {tickers_str}",
            "output_summary": "",
            "details": list(details),
            "data": None,
            "duration_ms": int((time.time() - start) * 1000),
        })

    total_articles = sum(len(s.get("articles", [])) for s in sentiment_map.values())
    overall_bullish = sum(s.get("bullish_pct", 50) for s in sentiment_map.values())
    avg_bullish = int(overall_bullish / len(sentiment_map)) if sentiment_map else 50

    duration = int((time.time() - start) * 1000)
    await emit({
        "step_id": "news_agent",
        "step_name": "News & Sentiment",
        "status": "done",
        "icon": "📰",
        "input_summary": f"Analyzed news for {len(tickers)} stocks",
        "output_summary": f"Found {total_articles} articles. Sentiment: {avg_bullish}% Bullish",
        "details": details,
        "data": {"sentiment_summary": {k: v["overall"] for k, v in sentiment_map.items()}},
        "duration_ms": duration,
    })

    return sentiment_map
