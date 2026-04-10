import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


def fetch_news(ticker: str, max_results: int = 5) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return []
    try:
        client = TavilyClient(api_key=api_key)
        clean_ticker = ticker.replace(".NS", "").replace(".BO", "")
        query = f"{clean_ticker} NSE stock news latest"
        response = client.search(query=query, max_results=max_results, search_depth="basic")
        articles = []
        for r in response.get("results", []):
            articles.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", "")[:200],
            })
        return articles
    except Exception as e:
        return [{"title": f"Error fetching news: {str(e)}", "url": "", "snippet": ""}]
