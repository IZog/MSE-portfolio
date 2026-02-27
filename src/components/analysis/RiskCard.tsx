import type { RiskAssessment } from '../../types';
import Card from '../common/Card';

interface Props {
  risk: RiskAssessment;
}

function severityStyle(severity: string | null): string {
  if (!severity) return 'bg-gray-100 text-gray-800';
  const lower = severity.toLowerCase();
  if (lower === 'low') return 'bg-green-100 text-green-800';
  if (lower === 'medium') return 'bg-yellow-100 text-yellow-800';
  if (lower === 'high') return 'bg-orange-100 text-orange-800';
  if (lower.includes('very high')) return 'bg-red-100 text-red-800';
  return 'bg-gray-100 text-gray-800';
}

function overallBadge(risk: string | null): string {
  if (!risk) return 'bg-gray-600';
  const lower = risk.toLowerCase();
  if (lower === 'low') return 'bg-green-600';
  if (lower === 'medium') return 'bg-yellow-500';
  if (lower === 'high') return 'bg-orange-500';
  return 'bg-red-600';
}

const RISK_LABELS: { key: keyof Pick<RiskAssessment, 'liquidity_risk' | 'volatility_risk' | 'financial_risk' | 'market_risk'>; label: string }[] = [
  { key: 'liquidity_risk', label: 'Liquidity' },
  { key: 'volatility_risk', label: 'Volatility' },
  { key: 'financial_risk', label: 'Financial' },
  { key: 'market_risk', label: 'Market' },
];

export default function RiskCard({ risk }: Props) {
  return (
    <Card title="Risk Assessment">
      <div className="mb-4">
        <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold text-white ${overallBadge(risk.overall_risk)}`}>
          {risk.overall_risk ?? 'N/A'} Risk
        </span>
      </div>

      <div className="space-y-2 mb-4">
        {RISK_LABELS.map(({ key, label }) => {
          const value = risk[key];
          return (
            <div key={key} className="flex items-center justify-between text-sm">
              <span className="text-gray-700">{label}</span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${severityStyle(value ?? null)}`}>
                {value ?? 'N/A'}
              </span>
            </div>
          );
        })}
      </div>

      {risk.factors.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Risk Factors</h4>
          <ul className="space-y-1">
            {risk.factors.map((factor, i) => (
              <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                <span className="text-orange-400 mt-0.5 flex-shrink-0">&#9679;</span>
                {factor}
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  );
}
