import type { FinancialData, FinancialRatios, ValuationMetrics } from '../../types';
import { formatMillionsMKD, formatPercent, formatRatio } from '../../utils/format';
import Card from '../common/Card';

interface Props {
  financials: FinancialData[];
  ratios: FinancialRatios;
  valuation: ValuationMetrics;
}

export default function FundamentalsCard({ financials, ratios, valuation }: Props) {
  const latest = financials.length > 0
    ? financials.reduce((a, b) => (a.year > b.year ? a : b))
    : null;

  const rows = [
    { label: 'Revenue', value: latest?.revenue != null ? formatMillionsMKD(latest.revenue) : 'N/A' },
    { label: 'Net Profit', value: latest?.net_profit != null ? formatMillionsMKD(latest.net_profit) : 'N/A' },
    { label: 'Net Margin', value: valuation.net_profit_margin != null ? formatPercent(valuation.net_profit_margin) : 'N/A' },
    { label: 'Equity', value: latest?.equity != null ? formatMillionsMKD(latest.equity) : 'N/A' },
    { label: 'ROA', value: ratios.roa != null ? formatPercent(ratios.roa) : 'N/A' },
    { label: 'ROE', value: ratios.roe != null ? formatPercent(ratios.roe) : 'N/A' },
    { label: 'EPS', value: ratios.eps != null ? `${formatRatio(ratios.eps)} MKD` : 'N/A' },
    { label: 'Book Value/Share', value: ratios.book_value_per_share != null ? `${formatRatio(ratios.book_value_per_share)} MKD` : 'N/A' },
  ];

  return (
    <Card title={`Fundamentals${latest ? ` (${latest.year})` : ''}`}>
      <dl className="space-y-2 text-sm">
        {rows.map((r) => (
          <div key={r.label} className="flex justify-between">
            <dt className="text-gray-500">{r.label}</dt>
            <dd className="text-gray-900 font-medium">{r.value}</dd>
          </div>
        ))}
      </dl>
    </Card>
  );
}
