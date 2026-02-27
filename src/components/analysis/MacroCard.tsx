import type { MacroContext, TechnicalAnalysis } from '../../types';
import { formatRatio, formatPercent } from '../../utils/format';
import Card from '../common/Card';

interface Props {
  macro: MacroContext;
  technical?: TechnicalAnalysis;
}

export default function MacroCard({ macro, technical }: Props) {
  const mbi10YtdColor = macro.mbi10_ytd_pct != null && macro.mbi10_ytd_pct >= 0 ? 'text-green-600' : 'text-red-600';

  const rows = [
    { label: 'MBI10 Index', value: macro.mbi10_value != null ? formatRatio(macro.mbi10_value) : 'N/A' },
    {
      label: 'MBI10 YTD',
      value: macro.mbi10_ytd_pct != null ? formatPercent(macro.mbi10_ytd_pct) : 'N/A',
      colorClass: macro.mbi10_ytd_pct != null ? mbi10YtdColor : undefined,
    },
    { label: 'GDP Growth', value: macro.gdp_growth != null ? formatPercent(macro.gdp_growth) : 'N/A' },
    { label: 'Inflation', value: macro.inflation != null ? formatPercent(macro.inflation) : 'N/A' },
    { label: 'Policy Rate', value: macro.policy_rate != null ? formatPercent(macro.policy_rate) : 'N/A' },
    { label: 'Deposit Rate', value: macro.deposit_rate != null ? formatPercent(macro.deposit_rate) : 'N/A' },
  ];

  if (technical?.beta_vs_mbi10 != null) {
    rows.push({
      label: 'Beta vs MBI10',
      value: formatRatio(technical.beta_vs_mbi10),
      colorClass: undefined,
    });
  }

  return (
    <Card title="Macro Context">
      <dl className="space-y-2">
        {rows.map((r) => (
          <div key={r.label} className="flex justify-between text-sm">
            <dt className="text-gray-500">{r.label}</dt>
            <dd className={`font-medium ${(r as { colorClass?: string }).colorClass ?? 'text-gray-900'}`}>{r.value}</dd>
          </div>
        ))}
      </dl>
    </Card>
  );
}
