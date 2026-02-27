import type { RiskAssessment, TechnicalAnalysis } from '../../types';
import { formatNumber } from '../../utils/format';
import Card from '../common/Card';

interface Props {
  risk: RiskAssessment;
  technical: TechnicalAnalysis;
}

function flagStyle(flag: string | null): string {
  if (!flag) return 'text-gray-500';
  const lower = flag.toLowerCase();
  if (lower.includes('active') || lower === 'low') return 'text-green-600';
  if (lower.includes('caution') || lower === 'medium') return 'text-amber-600';
  if (lower.includes('stale') || lower.includes('high') || lower.includes('very high')) return 'text-red-600';
  return 'text-gray-600';
}

export default function LiquidityFlagsCard({ risk, technical }: Props) {
  const flags = [
    {
      label: 'Avg Volume (10d)',
      value: technical.avg_volume_10d != null ? formatNumber(technical.avg_volume_10d) : 'N/A',
      flag: risk.liquidity_risk,
    },
    {
      label: 'Days Since Last Trade',
      value: technical.days_since_last_trade != null ? `${technical.days_since_last_trade} days` : 'N/A',
      flag: risk.days_since_last_trade_flag,
    },
    {
      label: 'Free Float',
      value: risk.free_float_flag ?? 'Unknown',
      flag: null,
    },
    {
      label: 'Ownership Concentration',
      value: risk.ownership_concentration_flag ?? 'Unknown',
      flag: null,
    },
  ];

  return (
    <Card title="Liquidity & Risk Flags">
      <dl className="space-y-3 text-sm">
        {flags.map((f) => (
          <div key={f.label} className="flex justify-between items-center">
            <dt className="text-gray-500">{f.label}</dt>
            <dd className="text-right">
              <span className="text-gray-900 font-medium">{f.value}</span>
              {f.flag && (
                <span className={`ml-2 text-xs font-semibold ${flagStyle(f.flag)}`}>
                  {f.flag}
                </span>
              )}
            </dd>
          </div>
        ))}
      </dl>
    </Card>
  );
}
