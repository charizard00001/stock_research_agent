import { motion } from 'framer-motion';
import { Download, TrendingUp, AlertTriangle, ArrowRightLeft } from 'lucide-react';
import StockCard from './StockCard';
import ChatPanel from './ChatPanel';
import type { AnalysisResult } from '../types';

interface Props {
  result: AnalysisResult;
  sessionId: string;
}

export default function ReportDashboard({ result, sessionId }: Props) {
  const { report, portfolio, macro } = result;
  const pnlPositive = portfolio.total_pnl_pct >= 0;

  const handleDownloadPdf = () => {
    window.open(`/api/export-pdf?session_id=${encodeURIComponent(sessionId)}`, '_blank');
  };

  // Recommendation badge color
  const recText = report.overall_recommendation?.toUpperCase() || '';
  const recColor = recText.includes('BUY') || recText.includes('ACCUMULATE')
    ? 'text-green-600 bg-green-50 border-green-200'
    : recText.includes('SELL') || recText.includes('EXIT')
    ? 'text-red-600 bg-red-50 border-red-200'
    : 'text-amber-600 bg-amber-50 border-amber-200';

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="w-full max-w-3xl mx-auto space-y-6"
    >
      {/* Portfolio Summary — horizontal stat row */}
      <div className="flex items-center divide-x divide-gray-200 py-4">
        <StatBlock
          label="Portfolio Value"
          value={`₹${portfolio.total_value.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
        />
        <StatBlock
          label="Invested"
          value={`₹${portfolio.total_invested.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
        />
        <StatBlock
          label="P&L"
          value={`${pnlPositive ? '+' : ''}${portfolio.total_pnl_pct.toFixed(2)}%`}
          valueColor={pnlPositive ? 'text-green-600' : 'text-red-600'}
        />
        <StatBlock
          label="Health Score"
          value={`${report.health_score}/100`}
          valueColor={report.health_score >= 70 ? 'text-green-600' : report.health_score >= 40 ? 'text-amber-600' : 'text-red-600'}
          subtitle={report.health_score_reason}
        />
      </div>

      {/* Recommendation */}
      <div className={`p-5 border ${recColor}`}>
        <div className="flex items-center gap-3">
          <span className={`text-xs font-semibold uppercase tracking-wider px-3 py-1 border ${recColor}`}>
            {report.overall_recommendation}
          </span>
        </div>
        {report.executive_summary && (
          <p className="text-sm text-[#6B7280] mt-3 leading-relaxed max-w-3xl line-clamp-2">
            {report.executive_summary.split('.').slice(0, 2).join('.') + '.'}
          </p>
        )}
      </div>

      {/* Executive Summary */}
      <SectionCard title="Executive Summary">
        <p className="text-sm text-[#6B7280] leading-[1.7]">{report.executive_summary}</p>
      </SectionCard>

      {/* Tomorrow's Outlook */}
      <SectionCard title="Tomorrow's Outlook">
        <p className="text-sm text-[#6B7280] leading-[1.7]">{report.tomorrow_outlook}</p>
      </SectionCard>

      {/* Macro Context */}
      {macro.macro_summary && (
        <SectionCard title="Macro Context">
          <p className="text-sm text-[#6B7280] leading-[1.7] whitespace-pre-line">{macro.macro_summary}</p>
        </SectionCard>
      )}

      {/* Stock Analysis — stacked vertically */}
      <div>
        <h3 className="text-sm font-semibold uppercase tracking-wide text-[#6B7280] mb-4">Stock Analysis</h3>
        <div className="space-y-4">
          {report.stocks.map(stock => (
            <StockCard key={stock.ticker} stock={stock} />
          ))}
        </div>
      </div>

      {/* Opportunities */}
      {report.top_opportunities.length > 0 && (
        <SectionCard title="Opportunities" icon={<TrendingUp className="h-4 w-4 text-green-500" strokeWidth={1.5} />}>
          <ul className="space-y-2.5">
            {report.top_opportunities.map((opp, i) => (
              <li key={i} className="text-[13px] text-[#6B7280] flex items-start gap-2.5 leading-relaxed">
                <span className="text-green-500 mt-0.5 shrink-0">+</span> {opp}
              </li>
            ))}
          </ul>
        </SectionCard>
      )}

      {/* Risks */}
      {report.top_risks.length > 0 && (
        <SectionCard title="Risks" icon={<AlertTriangle className="h-4 w-4 text-red-500" strokeWidth={1.5} />}>
          <ul className="space-y-2.5">
            {report.top_risks.map((risk, i) => (
              <li key={i} className="text-[13px] text-[#6B7280] flex items-start gap-2.5 leading-relaxed">
                <span className="text-red-500 mt-0.5 shrink-0">–</span> {risk}
              </li>
            ))}
          </ul>
        </SectionCard>
      )}

      {/* Rebalancing */}
      {report.rebalancing_suggestions.length > 0 && (
        <SectionCard title="Rebalancing Suggestions" icon={<ArrowRightLeft className="h-4 w-4 text-green-500" strokeWidth={1.5} />}>
          <ul className="space-y-2.5">
            {report.rebalancing_suggestions.map((sug, i) => (
              <li key={i} className="text-[13px] text-[#6B7280] flex items-start gap-2.5 leading-relaxed">
                <span className="text-green-500 mt-0.5 shrink-0">→</span> {sug}
              </li>
            ))}
          </ul>
        </SectionCard>
      )}

      {/* Chat */}
      <ChatPanel sessionId={sessionId} />

      {/* Footer */}
      <div className="flex flex-col items-center gap-5 pt-2 pb-12">
        <button
          onClick={handleDownloadPdf}
          className="inline-flex items-center gap-2 px-6 py-2 bg-green-500 text-white font-medium text-sm hover:bg-green-600 transition-all duration-200"
        >
          <Download className="h-4 w-4" strokeWidth={1.5} /> Download PDF Report
        </button>
        <p className="text-[11px] text-[#9CA3AF] text-center max-w-md leading-relaxed">
          AI-generated analysis for informational purposes only. Not financial advice.
          Always consult a qualified financial advisor before making investment decisions.
        </p>
      </div>
    </motion.div>
  );
}

/* ---- Reusable primitives ---- */

function SectionCard({ title, children, icon }: { title: string; children: React.ReactNode; icon?: React.ReactNode }) {
  return (
    <div className="border border-gray-200 border-l-4 border-l-green-400 p-5 mb-4 bg-white">
      <h3 className="text-sm font-semibold text-[#111827] mb-3 flex items-center gap-2">
        {icon}
        {title}
      </h3>
      {children}
    </div>
  );
}

function StatBlock({ label, value, valueColor = 'text-[#111827]', subtitle }: { label: string; value: string; valueColor?: string; subtitle?: string }) {
  return (
    <div className="flex-1 px-5 first:pl-0 last:pr-0">
      <p className="text-xs text-[#9CA3AF] mb-1">{label}</p>
      <p className={`text-lg font-bold tracking-[-0.02em] ${valueColor}`} style={{ fontFamily: 'var(--font-mono)' }}>{value}</p>
      {subtitle && <p className="text-[11px] text-[#6B7280] mt-0.5 line-clamp-2">{subtitle}</p>}
    </div>
  );
}
