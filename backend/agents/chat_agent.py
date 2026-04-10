import json


def build_chat_system_prompt(session_data: dict) -> str:
    """Build a system prompt that injects full portfolio context for the chat LLM."""
    report = session_data.get("report", {})
    portfolio = session_data.get("portfolio", {})
    macro = session_data.get("macro", {})

    # Portfolio summary
    portfolio_summary = (
        f"Total Value: ₹{portfolio.get('total_value', 0):,.2f}\n"
        f"Total Invested: ₹{portfolio.get('total_invested', 0):,.2f}\n"
        f"Overall P&L: {portfolio.get('total_pnl_pct', 0):.2f}%\n"
        f"Health Score: {report.get('health_score', 'N/A')}/100 — {report.get('health_score_reason', '')}\n"
        f"Overall Recommendation: {report.get('overall_recommendation', 'N/A')}"
    )

    # Per-stock details
    stock_lines = []
    for s in report.get("stocks", []):
        line = (
            f"- {s.get('ticker')} ({s.get('company_name', '')}): "
            f"Price ₹{s.get('current_price', 'N/A')}, "
            f"Day Change {s.get('day_change_pct', 0):.2f}%, "
            f"Avg Buy ₹{s.get('avg_buy_price', 'N/A')}, "
            f"Qty {s.get('quantity', 'N/A')}, "
            f"P&L {s.get('pnl_pct', 0):.2f}%, "
            f"Weight {s.get('portfolio_weight_pct', 0):.1f}%, "
            f"RSI {s.get('rsi', 'N/A')}, "
            f"MACD {s.get('macd_crossover', 'N/A')}, "
            f"Signal {s.get('technical_signal', 'N/A')}, "
            f"Rating {s.get('analyst_rating', 'N/A')}, "
            f"Action {s.get('action', 'N/A')}: {s.get('action_reason', '')}, "
            f"Tomorrow {s.get('tomorrow_direction', 'N/A')} "
            f"(₹{s.get('tomorrow_range', {}).get('low', '?')}–₹{s.get('tomorrow_range', {}).get('high', '?')}), "
            f"News Sentiment {s.get('news_sentiment', 'N/A')}"
        )
        stock_lines.append(line)
    stocks_block = "\n".join(stock_lines) if stock_lines else "No stock data available."

    # Macro
    nifty = macro.get("nifty", {})
    sensex = macro.get("sensex", {})
    macro_block = (
        f"Nifty: {nifty.get('price', 'N/A')} ({nifty.get('change_pct', 0):.2f}%)\n"
        f"Sensex: {sensex.get('price', 'N/A')} ({sensex.get('change_pct', 0):.2f}%)\n"
        f"{macro.get('macro_summary', '')}"
    )

    # Report sections
    exec_summary = report.get("executive_summary", "")
    tomorrow_outlook = report.get("tomorrow_outlook", "")
    opportunities = "\n".join(f"  + {o}" for o in report.get("top_opportunities", []))
    risks = "\n".join(f"  - {r}" for r in report.get("top_risks", []))
    rebalancing = "\n".join(f"  → {s}" for s in report.get("rebalancing_suggestions", []))

    return f"""You are Equilyze, an AI portfolio analyst assistant. You help users understand their portfolio, answer questions about their stocks, and provide actionable insights.

You have access to the user's complete portfolio analysis data below. Answer questions based ONLY on this data. Be specific — cite exact numbers, prices, percentages. If the data doesn't contain information to answer a question, say so honestly.

Keep responses concise and conversational. Use bullet points for lists. Bold key numbers or tickers when helpful.

IMPORTANT: You are NOT a financial advisor. Always remind the user (briefly, at the end if the question is about trading decisions) that this is AI-generated analysis and not financial advice.

---
PORTFOLIO SUMMARY:
{portfolio_summary}

EXECUTIVE SUMMARY:
{exec_summary}

TOMORROW'S OUTLOOK:
{tomorrow_outlook}

STOCK HOLDINGS:
{stocks_block}

MACRO CONTEXT:
{macro_block}

OPPORTUNITIES:
{opportunities}

RISKS:
{risks}

REBALANCING SUGGESTIONS:
{rebalancing}
---"""
