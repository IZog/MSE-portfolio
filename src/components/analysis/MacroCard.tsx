import type { MacroContext } from '../../types';
import { formatRatio, formatPercent } from '../../utils/format';
import Card from '../common/Card';

interface Props {
  macro: MacroContext;
}

export default function MacroCard({ macro }: Props) {
  const rows = [
    { label: 'MBI10 Index', value: macro.mbi10_value != null ? formatRatio(macro.mbi10_value) : 'N/A' },
    { label: 'GDP Growth', value: macro.gdp_growth != null ? formatPercent(macro.gdp_growth) : 'N/A' },
    { label: 'Inflation', value: macro.inflation != null ? formatPercent(macro.inflation) : 'N/A' },
    { label: 'Policy Rate', value: macro.policy_rate != null ? formatPercent(macro.policy_rate) : 'N/A' },
  ];

  return (
    <Card title="Macro Context">
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
