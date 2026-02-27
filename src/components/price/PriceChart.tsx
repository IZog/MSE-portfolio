import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import type { PricePoint, TechnicalAnalysis } from '../../types';
import Card from '../common/Card';

interface Props {
  history: PricePoint[];
  technical?: TechnicalAnalysis;
}

export default function PriceChart({ history, technical }: Props) {
  const data = history.map((p) => ({
    date: p.date,
    price: p.last_trade_price,
  }));

  return (
    <Card title="Price History">
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              tickFormatter={(v: string) => {
                const d = new Date(v);
                return `${d.getMonth() + 1}/${d.getDate()}`;
              }}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 11, fill: '#94a3b8' }}
              domain={['auto', 'auto']}
              tickFormatter={(v: number) => v.toLocaleString()}
            />
            <Tooltip
              contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}
              formatter={(value: unknown) => [`${Number(value).toLocaleString()} MKD`, 'Price']}
              labelFormatter={(label: unknown) => new Date(String(label)).toLocaleDateString()}
            />
            {technical?.support != null && (
              <ReferenceLine
                y={technical.support}
                stroke="#22c55e"
                strokeDasharray="4 4"
                label={{ value: 'Support', position: 'right', fontSize: 10, fill: '#22c55e' }}
              />
            )}
            {technical?.resistance != null && (
              <ReferenceLine
                y={technical.resistance}
                stroke="#ef4444"
                strokeDasharray="4 4"
                label={{ value: 'Resistance', position: 'right', fontSize: 10, fill: '#ef4444' }}
              />
            )}
            <Line
              type="monotone"
              dataKey="price"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
