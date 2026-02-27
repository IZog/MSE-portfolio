import type { ValuationMetrics } from '../../types';
import { formatPercent, formatRatio } from '../../utils/format';
import Card from '../common/Card';

interface Props {
  valuation: ValuationMetrics;
}

function assessmentBadge(assessment: string | null): string {
  if (!assessment) return 'bg-gray-100 text-gray-700 border-gray-200';
  const lower = assessment.toLowerCase();
  if (lower.includes('undervalued') || lower.includes('attractive') || lower.includes('good') || lower.includes('low'))
    return 'bg-green-50 text-green-700 border-green-200';
  if (lower.includes('overvalued') || lower.includes('expensive') || lower.includes('high'))
    return 'bg-red-50 text-red-700 border-red-200';
  return 'bg-amber-50 text-amber-700 border-amber-200';
}

export default function ValuationCard({ valuation }: Props) {
  return (
    <Card title="Valuation">
      {valuation.overall_assessment && (
        <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold border mb-4 ${assessmentBadge(valuation.overall_assessment)}`}>
          {valuation.overall_assessment}
        </div>
      )}

      <dl className="space-y-2 text-sm">
        <div className="flex justify-between items-center">
          <dt className="text-gray-500">P/E Ratio</dt>
          <dd className="flex items-center gap-2">
            <span className="text-gray-900 font-medium">
              {valuation.pe_ratio != null ? formatRatio(valuation.pe_ratio) : 'N/A'}
            </span>
            {valuation.pe_assessment && (
              <span className={`px-2 py-0.5 rounded text-xs font-medium border ${assessmentBadge(valuation.pe_assessment)}`}>
                {valuation.pe_assessment}
              </span>
            )}
          </dd>
        </div>
        <div className="flex justify-between items-center">
          <dt className="text-gray-500">P/B Ratio</dt>
          <dd className="flex items-center gap-2">
            <span className="text-gray-900 font-medium">
              {valuation.pb_ratio != null ? formatRatio(valuation.pb_ratio) : 'N/A'}
            </span>
            {valuation.pb_assessment && (
              <span className={`px-2 py-0.5 rounded text-xs font-medium border ${assessmentBadge(valuation.pb_assessment)}`}>
                {valuation.pb_assessment}
              </span>
            )}
          </dd>
        </div>
        <div className="flex justify-between items-center">
          <dt className="text-gray-500">Dividend Yield</dt>
          <dd className="flex items-center gap-2">
            <span className="text-gray-900 font-medium">
              {valuation.dividend_yield != null ? formatPercent(valuation.dividend_yield) : 'N/A'}
            </span>
            {valuation.dividend_assessment && (
              <span className={`px-2 py-0.5 rounded text-xs font-medium border ${assessmentBadge(valuation.dividend_assessment)}`}>
                {valuation.dividend_assessment}
              </span>
            )}
          </dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-gray-500">Earnings Yield</dt>
          <dd className="text-gray-900 font-medium">
            {valuation.earnings_yield != null ? formatPercent(valuation.earnings_yield) : 'N/A'}
          </dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-gray-500">Score</dt>
          <dd className="text-gray-900 font-bold">{valuation.score}<span className="text-gray-400 font-normal">/100</span></dd>
        </div>
      </dl>
    </Card>
  );
}
