interface Article {
  headline?: string;
  title?: string;
  sentiment?: string;
  impact_score?: number;
  brief_reason?: string;
}

interface Props {
  articles: Article[];
}

export default function NewsPanel({ articles }: Props) {
  if (!articles || articles.length === 0) return null;

  const sentimentColor = (s?: string) => {
    if (s === 'BULLISH') return 'text-green-600';
    if (s === 'BEARISH') return 'text-red-500';
    return 'text-[#9CA3AF]';
  };

  const sentimentDot = (s?: string) => {
    if (s === 'BULLISH') return 'bg-green-500';
    if (s === 'BEARISH') return 'bg-red-500';
    return 'bg-[#9CA3AF]';
  };

  return (
    <div className="space-y-2">
      {articles.slice(0, 3).map((a, i) => (
        <div key={i} className="flex items-start gap-2.5 text-xs">
          <span className={`w-1.5 h-1.5 mt-1.5 shrink-0 ${sentimentDot(a.sentiment)}`} />
          <span className={`leading-relaxed ${sentimentColor(a.sentiment)}`}>
            {a.headline || a.title || 'Untitled'}
          </span>
        </div>
      ))}
    </div>
  );
}
