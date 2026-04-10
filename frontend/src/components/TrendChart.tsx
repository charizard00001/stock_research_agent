import { AreaChart, Area, ResponsiveContainer, YAxis } from 'recharts';

interface Props {
  data: number[];
  color?: string;
  height?: number;
}

export default function TrendChart({ data, color, height = 36 }: Props) {
  if (!data || data.length < 2) return null;

  const chartData = data.map((value, i) => ({ i, value }));
  const isPositive = data[data.length - 1] >= data[0];
  const chartColor = color || (isPositive ? '#22C55E' : '#EF4444');

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={chartData}>
        <defs>
          <linearGradient id={`grad-${chartColor}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={chartColor} stopOpacity={0.15} />
            <stop offset="100%" stopColor={chartColor} stopOpacity={0} />
          </linearGradient>
        </defs>
        <YAxis domain={['dataMin', 'dataMax']} hide />
        <Area
          type="monotone"
          dataKey="value"
          stroke={chartColor}
          strokeWidth={1.25}
          fill={`url(#grad-${chartColor})`}
          dot={false}
          isAnimationActive={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
