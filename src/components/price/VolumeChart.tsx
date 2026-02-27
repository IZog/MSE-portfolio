import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import type { PricePoint } from '../../types';
import Card from '../common/Card';

interface Props {
  history: PricePoint[];
}

export default function VolumeChart({ history }: Props) {
  const data = history.map((p) => ({
    date: p.date,
    volume: p.volume,
  }));

  return (
    <Card title="Volume">
      <div className="h-40">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10, fill: '#94a3b8' }}
              tickFormatter={(v: string) => {
                const d = new Date(v);
                return `${d.getMonth() + 1}/${d.getDate()}`;
              }}
              interval="preserveStartEnd"
            />
            <YAxis
              tick={{ fontSize: 10, fill: '#94a3b8' }}
              tickFormatter={(v: number) => {
                if (v >= 1000) return `${(v / 1000).toFixed(0)}K`;
                return v.toString();
              }}
            />
            <Tooltip
              contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}
              formatter={(value: unknown) => [Number(value).toLocaleString(), 'Volume']}
              labelFormatter={(label: unknown) => new Date(String(label)).toLocaleDateString()}
            />
            <Bar dataKey="volume" fill="#94a3b8" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
