export interface AgentStep {
  step_id: string;
  step_name: string;
  status: 'pending' | 'running' | 'done' | 'error';
  icon: string;
  input_summary: string;
  output_summary: string;
  details: string[];
  data: Record<string, unknown> | null;
  duration_ms: number;
  timestamp?: string;
}

export interface StockTomorrow {
  low: number;
  high: number;
}

export interface StockReportData {
  ticker: string;
  company_name: string;
  analyst_rating: string;
  rating_reason: string;
  tomorrow_range: StockTomorrow;
  tomorrow_direction: string;
  key_catalysts: string[];
  key_risks: string[];
  action: string;
  action_reason: string;
  current_price?: number;
  day_change_pct?: number;
  avg_buy_price?: number;
  quantity?: number;
  pnl_pct?: number;
  current_value?: number;
  portfolio_weight_pct?: number;
  sparkline?: number[];
  rsi?: number;
  macd_crossover?: string;
  technical_signal?: string;
  news_sentiment?: string;
  news_articles?: Array<{
    headline?: string;
    title?: string;
    sentiment?: string;
    impact_score?: number;
    brief_reason?: string;
  }>;
}

export interface Report {
  executive_summary: string;
  health_score: number;
  health_score_reason: string;
  tomorrow_outlook: string;
  overall_recommendation: string;
  stocks: StockReportData[];
  top_opportunities: string[];
  top_risks: string[];
  rebalancing_suggestions: string[];
}

export interface PortfolioData {
  total_value: number;
  total_invested: number;
  total_pnl_pct: number;
  holdings: Array<Record<string, unknown>>;
}

export interface MacroData {
  nifty: { price: number; change_pct: number };
  sensex: { price: number; change_pct: number };
  macro_summary: string;
}

export interface AnalysisResult {
  report: Report;
  portfolio: PortfolioData;
  macro: MacroData;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}
