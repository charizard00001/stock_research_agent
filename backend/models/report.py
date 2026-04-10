from pydantic import BaseModel
from typing import Optional


class StockTomorrow(BaseModel):
    low: float = 0.0
    high: float = 0.0


class StockReport(BaseModel):
    ticker: str
    company_name: str = ""
    analyst_rating: str = "HOLD"
    rating_reason: str = ""
    tomorrow_range: StockTomorrow = StockTomorrow()
    tomorrow_direction: str = "SIDEWAYS"
    key_catalysts: list[str] = []
    key_risks: list[str] = []
    action: str = "HOLD"
    action_reason: str = ""


class FullReport(BaseModel):
    executive_summary: str = ""
    health_score: int = 50
    health_score_reason: str = ""
    tomorrow_outlook: str = ""
    overall_recommendation: str = "STAY INVESTED"
    stocks: list[StockReport] = []
    top_opportunities: list[str] = []
    top_risks: list[str] = []
    rebalancing_suggestions: list[str] = []
