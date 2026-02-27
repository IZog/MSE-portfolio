import type { PriceData } from '../../types';
import { formatMKD, formatPercent, formatNumber } from '../../utils/format';
import Card from '../common/Card';

interface Props {
  price: PriceData;
}

export default function PriceCard({ price }: Props) {
  const changePct = price.price_change_pct ?? 0;
  const isPositive = changePct >= 0;
  const changeColor = isPositive ? 'text-green-600' : 'text-red-600';
  const changeBg = isPositive ? 'bg-green-50' : 'bg-red-50';

  // 52-week range position (0-100%)
  const high = price.high_52w ?? 0;
  const low = price.low_52w ?? 0;
  const current = price.current_price ?? 0;
  const range = high - low;
  const position = range > 0 ? ((current - low) / range) * 100 : 50;

  return (
    <Card title="Current Price">
      <div className="flex items-baseline gap-3 mb-3">
        <span className="text-3xl font-bold text-gray-900">
          {formatMKD(price.current_price)}
        </span>
        <span className={`text-sm font-medium px-2 py-0.5 rounded ${changeColor} ${changeBg}`}>
          {isPositive ? '+' : ''}{formatPercent(price.price_change_pct)}
        </span>
      </div>

      <dl className="space-y-1 text-sm mb-4">
        <div className="flex justify-between">
          <dt className="text-gray-500">Total Shares</dt>
          <dd className="text-gray-900 font-medium">{formatNumber(price.total_shares)}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-gray-500">Market Cap</dt>
          <dd className="text-gray-900 font-medium">{formatMKD(price.market_cap)}</dd>
        </div>
      </dl>

      <div className="mt-4">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>52W Low: {formatMKD(price.low_52w)}</span>
          <span>52W High: {formatMKD(price.high_52w)}</span>
        </div>
        <div className="relative h-2 bg-gray-200 rounded-full">
          <div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-red-400 via-yellow-400 to-green-400 rounded-full"
            style={{ width: '100%' }}
          />
          <div
            className="absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-[#0f172a] rounded-full border-2 border-white shadow"
            style={{ left: `${Math.min(Math.max(position, 0), 100)}%`, transform: 'translate(-50%, -50%)' }}
          />
        </div>
      </div>
    </Card>
  );
}
