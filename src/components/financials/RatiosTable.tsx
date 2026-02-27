import type { FinancialRatios } from '../../types';
import { formatRatio, formatPercent, formatMKD } from '../../utils/format';
import Card from '../common/Card';

interface Props {
  ratios: FinancialRatios;
}

export default function RatiosTable({ ratios }: Props) {
  const rows = [
    { label: 'P/E Ratio', value: formatRatio(ratios.pe_ratio) },
    { label: 'EPS', value: ratios.eps != null ? formatMKD(ratios.eps) : 'N/A' },
    { label: 'ROE', value: ratios.roe != null ? formatPercent(ratios.roe) : 'N/A' },
    { label: 'ROA', value: ratios.roa != null ? formatPercent(ratios.roa) : 'N/A' },
    { label: 'Book Value/Share', value: ratios.book_value_per_share != null ? formatMKD(ratios.book_value_per_share) : 'N/A' },
    { label: 'Dividend/Share', value: ratios.dividend_per_share != null ? formatMKD(ratios.dividend_per_share) : 'N/A' },
    { label: 'Dividend Yield', value: ratios.dividend_yield != null ? formatPercent(ratios.dividend_yield) : 'N/A' },
    { label: 'Market Cap', value: ratios.market_cap != null ? formatMKD(ratios.market_cap) : 'N/A' },
  ];

  return (
    <Card title="Financial Ratios">
      <dl className="space-y-2">
        {rows.map((r) => (
          <div key={r.label} className="flex justify-between text-sm">
            <dt className="text-gray-500">{r.label}</dt>
            <dd className="text-gray-900 font-medium">{r.value}</dd>
          </div>
        ))}
      </dl>
    </Card>
  );
}
