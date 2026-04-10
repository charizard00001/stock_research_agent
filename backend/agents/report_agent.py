import json
import time
from datetime import datetime
from backend.llm_client import chat

REPORT_SYSTEM = """You are a senior equity research analyst at Goldman Sachs India. You have been given complete portfolio data, technical indicators, news sentiment, and macro context.

Generate a comprehensive research report in the following EXACT JSON structure:

{
  "executive_summary": "3 sentence portfolio overview",
  "health_score": 0-100,
  "health_score_reason": "why this score",
  "tomorrow_outlook": "detailed paragraph on what to expect tomorrow",
  "overall_recommendation": "STAY INVESTED | PARTIAL BOOK | EXIT | ACCUMULATE",
  "stocks": [
    {
      "ticker": "RELIANCE.NS",
      "company_name": "Reliance Industries",
      "analyst_rating": "STRONG BUY | BUY | HOLD | SELL | STRONG SELL",
      "rating_reason": "2 sentence justification",
      "tomorrow_range": {"low": 2340, "high": 2410},
      "tomorrow_direction": "UP | DOWN | SIDEWAYS",
      "key_catalysts": ["catalyst 1", "catalyst 2"],
      "key_risks": ["risk 1", "risk 2"],
      "action": "HOLD | BUY MORE | PARTIAL SELL | SELL",
      "action_reason": "specific actionable reason"
    }
  ],
  "top_opportunities": ["opp1", "opp2", "opp3"],
  "top_risks": ["risk1", "risk2", "risk3"],
  "rebalancing_suggestions": ["suggestion1", "suggestion2"]
}

Return ONLY valid JSON. No markdown code fences. No backticks. No preamble. No explanation text before or after. Start your response with { and end with }."""

REPORT_PROMPT = """
You are a senior equity research analyst. Analyze this portfolio comprehensively.

PORTFOLIO DATA:
{portfolio_with_prices}

TECHNICAL INDICATORS:
{technicals}

NEWS SENTIMENT:
{news_sentiment}

MACRO CONTEXT:
{macro_summary}

TODAY'S DATE: {date}
MARKET: {market}

Your analysis must cover:
1. Is this portfolio well diversified? What sectors are overweight/underweight?
2. Which stocks have the strongest momentum going into tomorrow?
3. Which stocks face the highest risk tomorrow and why?
4. Based on news sentiment + technicals, what is the likely direction for each stock?
5. What is the overall portfolio health considering current market conditions?
6. What specific actions should the investor take before market opens tomorrow?

Be specific. Use actual numbers. Reference actual news. Make actionable recommendations.
Generate the JSON report as specified.
"""


async def run(enriched_holdings, technicals_map, sentiment_map, macro_data, emit, model=None):
    start = time.time()

    await emit({
        "step_id": "report_agent",
        "step_name": "Report Synthesis",
        "status": "running",
        "icon": "🧠",
        "input_summary": "Synthesizing all data into analyst report...",
        "output_summary": "",
        "details": ["Assembling portfolio context for LLM..."],
        "data": None,
        "duration_ms": 0,
    })

    # Build portfolio summary for prompt
    portfolio_lines = []
    for h in enriched_holdings:
        portfolio_lines.append(
            f"{h.yf_ticker} ({h.company_name}): Qty={h.quantity}, AvgBuy=₹{h.avg_buy_price}, "
            f"CMP=₹{h.current_price}, DayChg={h.day_change_pct:+.2f}%, P&L={h.pnl_pct:+.2f}%, "
            f"Value=₹{h.current_value:,.2f}, Weight={h.portfolio_weight_pct:.1f}%, "
            f"PE={h.pe_ratio}, Beta={h.beta}, 52wH=₹{h.high_52w}, 52wL=₹{h.low_52w}"
        )
    portfolio_text = "\n".join(portfolio_lines)

    # Build technicals summary
    tech_lines = []
    for ticker, t in technicals_map.items():
        tech_lines.append(
            f"{ticker}: Signal={t['signal']}, RSI={t['rsi']}, "
            f"MACD={t['macd']['crossover']}, SMA20={t['sma20']}, SMA50={t['sma50']}, "
            f"Bollinger={t['bollinger']['position']}"
        )
    technicals_text = "\n".join(tech_lines)

    # Build sentiment summary
    sent_lines = []
    for ticker, s in sentiment_map.items():
        articles_text = "; ".join([
            a.get("headline", a.get("title", ""))
            for a in s.get("scored_articles", s.get("articles", []))[:3]
        ])
        sent_lines.append(f"{ticker}: {s['overall']} ({s['bullish_pct']}% bullish) — {articles_text}")
    sentiment_text = "\n".join(sent_lines)

    macro_text = macro_data.get("macro_summary", "No macro data available")

    prompt = REPORT_PROMPT.format(
        portfolio_with_prices=portfolio_text,
        technicals=technicals_text,
        news_sentiment=sentiment_text,
        macro_summary=macro_text,
        date=datetime.now().strftime("%Y-%m-%d"),
        market="NSE/BSE India",
    )

    details = [
        "Assembling portfolio context for LLM...",
        f"Context size: {len(prompt)} chars",
        "Streaming report from LLM...",
    ]

    await emit({
        "step_id": "report_agent",
        "step_name": "Report Synthesis",
        "status": "running",
        "icon": "🧠",
        "input_summary": "Synthesizing all data into analyst report...",
        "output_summary": "",
        "details": list(details),
        "data": None,
        "duration_ms": int((time.time() - start) * 1000),
    })

    # Stream the report
    try:
        stream = chat(
            messages=[{"role": "user", "content": prompt}],
            system=REPORT_SYSTEM,
            stream=True,
            model=model,
        )

        full_response = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_response += token
                await emit({
                    "type": "REPORT_TOKEN",
                    "token": token,
                })

        # Parse the report JSON
        cleaned = full_response.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0]
        cleaned = cleaned.strip()

        # If still not valid JSON, try to extract JSON by finding outermost braces
        if not cleaned.startswith("{"):
            start_idx = cleaned.find("{")
            if start_idx != -1:
                cleaned = cleaned[start_idx:]

        if not cleaned.endswith("}"):
            end_idx = cleaned.rfind("}")
            if end_idx != -1:
                cleaned = cleaned[:end_idx + 1]

        cleaned = cleaned.strip()

        try:
            report_data = json.loads(cleaned)
        except json.JSONDecodeError as parse_err:
            # Last-resort: try to fix common issues like trailing commas
            import re
            fixed = re.sub(r',\s*([}\]])', r'\1', cleaned)
            try:
                report_data = json.loads(fixed)
            except json.JSONDecodeError:
                raise ValueError(
                    f"LLM returned invalid JSON. Parse error: {parse_err}. "
                    f"Response starts with: {cleaned[:200]}..."
                )

        details.append("✓ Report generated and parsed successfully")
        duration = int((time.time() - start) * 1000)

        await emit({
            "step_id": "report_agent",
            "step_name": "Report Synthesis",
            "status": "done",
            "icon": "🧠",
            "input_summary": "All pipeline data",
            "output_summary": f"Health Score: {report_data.get('health_score', 'N/A')}/100 | {report_data.get('overall_recommendation', 'N/A')}",
            "details": details,
            "data": None,
            "duration_ms": duration,
        })

        return report_data

    except Exception as e:
        details.append(f"❌ Report generation failed: {str(e)}")
        # Try to return raw text as fallback
        duration = int((time.time() - start) * 1000)
        await emit({
            "step_id": "report_agent",
            "step_name": "Report Synthesis",
            "status": "error",
            "icon": "🧠",
            "input_summary": "All pipeline data",
            "output_summary": f"Error: {str(e)}",
            "details": details,
            "data": None,
            "duration_ms": duration,
        })
        raise
