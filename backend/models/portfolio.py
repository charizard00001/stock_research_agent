from pydantic import BaseModel
from typing import Optional


class Holding(BaseModel):
    ticker: str
    quantity: float
    avg_buy_price: float
    exchange: str = "NSE"

    @property
    def yf_ticker(self) -> str:
        suffix = ".NS" if self.exchange.upper() == "NSE" else ".BO"
        t = self.ticker.upper()
        if not t.endswith((".NS", ".BO")):
            t = t + suffix
        return t


class EnrichedHolding(BaseModel):
    ticker: str
    yf_ticker: str
    company_name: str = ""
    quantity: float
    avg_buy_price: float
    exchange: str = "NSE"
    current_price: float = 0.0
    day_change_pct: float = 0.0
    high_52w: float = 0.0
    low_52w: float = 0.0
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    market_cap: Optional[float] = None
    beta: Optional[float] = None
    current_value: float = 0.0
    pnl_pct: float = 0.0
    portfolio_weight_pct: float = 0.0
    ohlcv: list = []


class Portfolio(BaseModel):
    session_id: str = ""
    holdings: list[Holding] = []
    enriched_holdings: list[EnrichedHolding] = []
    total_value: float = 0.0
    total_invested: float = 0.0
    total_pnl_pct: float = 0.0
