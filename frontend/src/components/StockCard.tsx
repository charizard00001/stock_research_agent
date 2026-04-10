import TrendChart from './TrendChart';
import NewsPanel from './NewsPanel';
import type { StockReportData } from '../types';

interface Props {
  stock: StockReportData;
}

const ratingStyle = (rating: string) => {
  const r = rating.toUpperCase();
  if (r.includes('STRONG BUY')) return 'text-green-700 bg-green-50 border-green-200';
  if (r.includes('BUY')) return 'text-green-600 bg-green-50 border-green-200';
  if (r.includes('HOLD')) return 'text-amber-600 bg-amber-50 border-amber-200';
  if (r.includes('SELL')) return 'text-red-600 bg-red-50 border-red-200';
  return 'text-[#9CA3AF] bg-[#F8FAF9] border-gray-200';
};

export default function StockCard({ stock }: Props) {
  const pnlPositive = (stock.pnl_pct ?? 0) >= 0;
  const dayPositive = (stock.day_change_pct ?? 0) >= 0;

  return (
    <div className="border border-gray-200 bg-white p-5 mb-4 transition-all duration-200 overflow-hidden">
      {/* Header: Name + Badge */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="font-semibold text-[15px] text-[#111827] tracking-[-0.01em]">{stock.ticker}</h4>
          <p className="text-xs text-[#9CA3AF] mt-0.5">{stock.company_name}</p>
        </div>
        <span className={`text-[10px] font-semibold px-2.5 py-1 border ${ratingStyle(stock.analyst_rating)}`}>
          {stock.analyst_rating}
        </span>
      </div>

      {/* Price + Change + RSI horizontal row */}
      <div className="flex items-baseline gap-4 mb-4">
        <span className="text-xl font-bold text-[#111827] tracking-[-0.02em]" style={{ fontFamily: 'var(--font-mono)' }}>
          ₹{stock.current_price?.toLocaleString('en-IN', { minimumFractionDigits: 2 }) ?? '—'}
        </span>
        <span className={`text-xs font-medium ${dayPositive ? 'text-green-600' : 'text-red-500'}`}>
          {dayPositive ? '+' : ''}{stock.day_change_pct?.toFixed(2) ?? 0}%
        </span>
        <span className="text-xs text-[#9CA3AF]">Avg ₹{stock.avg_buy_price?.toLocaleString('en-IN') ?? '—'}</span>
        <span className={`text-xs ${pnlPositive ? 'text-green-600' : 'text-red-500'}`}>
          P&L {pnlPositive ? '+' : ''}{stock.pnl_pct?.toFixed(2) ?? 0}%
        </span>
        {stock.rsi !== undefined && (
          <span className="text-xs text-[#9CA3AF]">RSI <span className="text-[#6B7280] font-mono">{stock.rsi}</span></span>
        )}
      </div>

      {/* Price chart — full width */}
      {stock.sparkline && stock.sparkline.length > 2 && (
        <div className="mb-4">
          <TrendChart data={stock.sparkline} height={60} />
        </div>
      )}

      {/* Tomorrow Range / Direction / MACD / Signal — 4-column grid */}
      <div className="grid grid-cols-4 gap-3 text-xs mb-4 p-3 bg-[#F8FAF9] border border-gray-200">
        <div>
          <span className="text-[#9CA3AF] block mb-1">Tomorrow Range</span>
          <span className="text-[#111827] font-mono">
            ₹{stock.tomorrow_range?.low?.toLocaleString('en-IN')} – ₹{stock.tomorrow_range?.high?.toLocaleString('en-IN')}
          </span>
        </div>
        <div>
          <span className="text-[#9CA3AF] block mb-1">Direction</span>
          <span className={`font-medium ${stock.tomorrow_direction === 'UP' ? 'text-green-600' : stock.tomorrow_direction === 'DOWN' ? 'text-red-500' : 'text-amber-600'}`}>
            {stock.tomorrow_direction}
          </span>
        </div>
        <div>
          <span className="text-[#9CA3AF] block mb-1">MACD</span>
          <span className={`font-medium ${stock.macd_crossover === 'BULLISH' ? 'text-green-600' : stock.macd_crossover === 'BEARISH' ? 'text-red-500' : 'text-[#6B7280]'}`}>
            {stock.macd_crossover || '—'}
          </span>
        </div>
        <div>
          <span className="text-[#9CA3AF] block mb-1">Signal</span>
          <span className="text-[#6B7280]">{stock.technical_signal || '—'}</span>
        </div>
      </div>

      {/* News */}
      {stock.news_articles && stock.news_articles.length > 0 && (
        <div className="mb-4 pt-4 border-t border-gray-200">
          <p className="text-[11px] text-[#9CA3AF] mb-2">Recent News</p>
          <NewsPanel articles={stock.news_articles} />
        </div>
      )}

      {/* AI Summary / Action */}
      <div className="bg-green-50 border-l-4 border-green-400 p-3">
        <div className="flex items-start gap-2.5">
          <span className={`text-[10px] font-semibold px-2 py-0.5 border shrink-0 mt-0.5 ${ratingStyle(stock.action || stock.analyst_rating)}`}>
            {stock.action}
          </span>
          <p className="text-[13px] text-[#6B7280] leading-relaxed">{stock.action_reason}</p>
        </div>
      </div>
    </div>
  );
}
