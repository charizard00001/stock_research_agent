import json
import time
from backend.llm_client import chat_with_image, chat
from backend.models.portfolio import Holding


OCR_PROMPT = """You are analyzing a screenshot of a stock portfolio from an Indian brokerage (Zerodha, Groww, Angel One, etc.).

Your task: Extract INDIVIDUAL STOCK HOLDINGS from the image.

CRITICAL RULES:
1. Only extract ACTUAL STOCK TICKERS (e.g., RELIANCE, TCS, INFY, HDFCBANK). 
2. Do NOT extract category labels like "Equity", "Mutual Funds", "Stocks", "ETF" as stock names.
3. If the screenshot shows a SUMMARY VIEW (only asset types like "Equity", "Mutual Funds" with totals), 
   respond with an empty array: []
4. Look for individual stock rows that show: stock name/ticker, quantity/shares, buy price, current price, P&L
5. Use the stock SYMBOL/TICKER, not the full company name (e.g., "RELIANCE" not "Reliance Industries Ltd")
6. Exchange defaults to NSE unless explicitly shown otherwise
7. If you see LTP/current price but no avg_buy_price, use LTP as avg_buy_price
8. quantity and avg_buy_price must be numbers

Return ONLY a JSON array with this exact format, no markdown, no preamble:
[{"ticker": "RELIANCE", "quantity": 10, "avg_buy_price": 2450.00, "exchange": "NSE"}]

If NO individual stocks are visible, return: []
"""


async def run(image_bytes: bytes, emit):
    start = time.time()
    await emit({
        "step_id": "ocr_agent",
        "step_name": "OCR & Portfolio Parse",
        "status": "running",
        "icon": "📸",
        "input_summary": "Processing uploaded screenshot...",
        "output_summary": "",
        "details": ["Sending image to vision model for OCR..."],
        "data": None,
        "duration_ms": 0,
    })

    try:
        response = chat_with_image(
            image_bytes=image_bytes,
            prompt=OCR_PROMPT,
            system="You are a financial data extraction assistant. Extract stock portfolio data from images accurately.",
        )
        raw_text = response.choices[0].message.content.strip()

        details = [
            "Sending image to vision model for OCR...",
            f"Received response ({len(raw_text)} chars)",
            "Parsing holdings from LLM response...",
        ]

        await emit({
            "step_id": "ocr_agent",
            "step_name": "OCR & Portfolio Parse",
            "status": "running",
            "icon": "📸",
            "input_summary": "Processing uploaded screenshot...",
            "output_summary": "",
            "details": details,
            "data": None,
            "duration_ms": int((time.time() - start) * 1000),
        })

        # Clean JSON from markdown fences
        cleaned = raw_text
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0]
        cleaned = cleaned.strip()

        holdings_data = json.loads(cleaned)

        if not holdings_data:
            raise ValueError(
                "No individual stock holdings found in the screenshot. "
                "Please upload a screenshot that shows individual stock names, quantities, and prices "
                "(e.g., your Holdings or Positions page, not the portfolio summary/overview page)."
            )

        holdings = [Holding(**h) for h in holdings_data]

        tickers_str = ", ".join([h.ticker for h in holdings])
        details.append(f"✓ Parsed {len(holdings)} holdings: {tickers_str}")

        duration = int((time.time() - start) * 1000)
        await emit({
            "step_id": "ocr_agent",
            "step_name": "OCR & Portfolio Parse",
            "status": "done",
            "icon": "📸",
            "input_summary": "screenshot.png",
            "output_summary": f"Parsed {len(holdings)} holdings: {tickers_str}",
            "details": details,
            "data": {"holdings": [h.model_dump() for h in holdings]},
            "duration_ms": duration,
        })

        return holdings

    except Exception as e:
        duration = int((time.time() - start) * 1000)
        await emit({
            "step_id": "ocr_agent",
            "step_name": "OCR & Portfolio Parse",
            "status": "error",
            "icon": "📸",
            "input_summary": "screenshot.png",
            "output_summary": f"Error: {str(e)}",
            "details": [f"❌ Failed to parse portfolio: {str(e)}"],
            "data": None,
            "duration_ms": duration,
        })
        raise
