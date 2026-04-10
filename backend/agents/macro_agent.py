import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from backend.llm_client import chat
from backend.tools.stock_data import get_index_data
from backend.tools.news_fetcher import fetch_news

executor = ThreadPoolExecutor(max_workers=3)

MACRO_PROMPT = """You are a macro analyst. Based on these data points, write a 3-paragraph market outlook
for tomorrow's Indian market session. Cover: global cues, domestic factors, key risks.

Data:
{macro_data}

Be specific with numbers. Reference the actual data provided. Keep it concise but actionable."""


async def run(emit, model=None):
    start = time.time()

    await emit({
        "step_id": "macro_agent",
        "step_name": "Macro Context",
        "status": "running",
        "icon": "🌍",
        "input_summary": "Fetching market indices and macro data",
        "output_summary": "",
        "details": ["Fetching Nifty 50 data..."],
        "data": None,
        "duration_ms": 0,
    })

    loop = asyncio.get_event_loop()
    details = ["Fetching Nifty 50 data..."]

    nifty = await loop.run_in_executor(executor, get_index_data, "^NSEI")
    details[-1] = f"✓ Nifty 50: {nifty['price']} ({nifty['change_pct']:+.2f}%)"
    details.append("Fetching Sensex data...")

    await emit({
        "step_id": "macro_agent",
        "step_name": "Macro Context",
        "status": "running",
        "icon": "🌍",
        "input_summary": "Fetching market indices and macro data",
        "output_summary": "",
        "details": list(details),
        "data": None,
        "duration_ms": int((time.time() - start) * 1000),
    })

    sensex = await loop.run_in_executor(executor, get_index_data, "^BSESN")
    details[-1] = f"✓ Sensex: {sensex['price']} ({sensex['change_pct']:+.2f}%)"
    details.append("Searching for market outlook news...")

    await emit({
        "step_id": "macro_agent",
        "step_name": "Macro Context",
        "status": "running",
        "icon": "🌍",
        "input_summary": "Fetching market indices and macro data",
        "output_summary": "",
        "details": list(details),
        "data": None,
        "duration_ms": int((time.time() - start) * 1000),
    })

    def fetch_macro_news():
        news1 = fetch_news("Indian stock market outlook tomorrow", max_results=3)
        news2 = fetch_news("FII DII flows today India", max_results=2)
        news3 = fetch_news("global market cues Asia", max_results=2)
        return news1 + news2 + news3

    macro_news = await loop.run_in_executor(executor, fetch_macro_news)
    details[-1] = f"✓ Found {len(macro_news)} macro news articles"
    details.append("Generating macro outlook via LLM...")

    await emit({
        "step_id": "macro_agent",
        "step_name": "Macro Context",
        "status": "running",
        "icon": "🌍",
        "input_summary": "Generating market outlook",
        "output_summary": "",
        "details": list(details),
        "data": None,
        "duration_ms": int((time.time() - start) * 1000),
    })

    macro_data = f"""
Nifty 50: {nifty['price']} (Day change: {nifty['change_pct']:+.2f}%)
Sensex: {sensex['price']} (Day change: {sensex['change_pct']:+.2f}%)

Recent Market News:
""" + "\n".join([f"- {n['title']}" for n in macro_news if n.get("title")])

    try:
        response = chat(
            messages=[{"role": "user", "content": MACRO_PROMPT.format(macro_data=macro_data)}],
            system="You are a senior macro market analyst covering Indian equity markets.",
            model=model,
        )
        macro_summary = response.choices[0].message.content.strip()
    except Exception as e:
        macro_summary = f"Unable to generate macro outlook: {str(e)}"

    details[-1] = "✓ Macro outlook generated"
    duration = int((time.time() - start) * 1000)

    await emit({
        "step_id": "macro_agent",
        "step_name": "Macro Context",
        "status": "done",
        "icon": "🌍",
        "input_summary": "Market indices + macro news",
        "output_summary": f"Nifty: {nifty['price']} | Sensex: {sensex['price']}",
        "details": details,
        "data": {
            "nifty": nifty,
            "sensex": sensex,
            "macro_summary": macro_summary,
        },
        "duration_ms": duration,
    })

    return {
        "nifty": nifty,
        "sensex": sensex,
        "macro_summary": macro_summary,
        "macro_news": macro_news,
    }
