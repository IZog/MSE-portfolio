import type { TechnicalAnalysis } from '../../types';
import { formatMKD } from '../../utils/format';
import Card from '../common/Card';

interface Props {
  technical: TechnicalAnalysis;
}

function trendIcon(trend: string | null): string {
  const lower = (trend ?? '').toLowerCase();
  if (lower.includes('bullish')) return '\u2191';
  if (lower.includes('bearish')) return '\u2193';
  return '\u2194';
}

function trendColor(trend: string | null): string {
  const lower = (trend ?? '').toLowerCase();
  if (lower.includes('bullish')) return 'text-green-600';
  if (lower.includes('bearish')) return 'text-red-600';
  return 'text-amber-600';
}

export default function TechnicalCard({ technical }: Props) {
  const position = technical.week52_position != null ? technical.week52_position : 50;

  return (
    <Card title="Technical Analysis">
      <div className="flex items-center gap-2 mb-4">
        <span className={`text-2xl ${trendColor(technical.trend)}`}>{trendIcon(technical.trend)}</span>
        <span className={`text-lg font-semibold ${trendColor(technical.trend)}`}>
          {technical.trend}
        </span>
      </div>

      <dl className="space-y-2 text-sm">
        <div className="flex justify-between">
          <dt className="text-gray-500">Support</dt>
          <dd className="text-green-700 font-medium">
            {technical.support != null ? formatMKD(technical.support) : 'N/A'}
          </dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-gray-500">Resistance</dt>
          <dd className="text-red-700 font-medium">
            {technical.resistance != null ? formatMKD(technical.resistance) : 'N/A'}
          </dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-gray-500">Momentum</dt>
          <dd className="text-gray-900">{technical.momentum ?? 'N/A'}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-gray-500">Volume Trend</dt>
          <dd className="text-gray-900">{technical.volume_trend ?? 'N/A'}</dd>
        </div>
      </dl>

      <div className="mt-4">
        <div className="text-xs text-gray-500 mb-1">52-Week Position</div>
        <div className="relative h-2 bg-gray-200 rounded-full">
          <div
            className="absolute top-0 left-0 h-full bg-blue-500 rounded-full"
            style={{ width: `${position}%` }}
          />
        </div>
        <div className="text-xs text-gray-500 text-right mt-0.5">{position.toFixed(0)}%</div>
      </div>
    </Card>
  );
}
