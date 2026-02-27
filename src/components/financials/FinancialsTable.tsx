import type { FinancialData } from '../../types';
import { formatMillionsMKD } from '../../utils/format';
import Card from '../common/Card';

interface Props {
  financials: FinancialData[];
}

export default function FinancialsTable({ financials }: Props) {
  const sorted = [...financials].sort((a, b) => b.year - a.year);

  return (
    <Card title="Financial Statements">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 text-xs uppercase">
              <th className="pb-2 pr-3">Year</th>
              <th className="pb-2 pr-3">Revenue</th>
              <th className="pb-2 pr-3">Op. Profit</th>
              <th className="pb-2 pr-3">Net Profit</th>
              <th className="pb-2 pr-3">Equity</th>
              <th className="pb-2 pr-3">Assets</th>
              <th className="pb-2">Liabilities</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((f) => (
              <tr key={f.year} className="border-t border-gray-50">
                <td className="py-2 pr-3 font-medium text-gray-900">{f.year}</td>
                <td className="py-2 pr-3 text-gray-700">{formatMillionsMKD(f.revenue)}</td>
                <td className="py-2 pr-3 text-gray-700">{formatMillionsMKD(f.operating_profit)}</td>
                <td className={`py-2 pr-3 font-medium ${(f.net_profit ?? 0) >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                  {formatMillionsMKD(f.net_profit)}
                </td>
                <td className="py-2 pr-3 text-gray-700">{formatMillionsMKD(f.equity)}</td>
                <td className="py-2 pr-3 text-gray-700">{formatMillionsMKD(f.total_assets)}</td>
                <td className="py-2 text-gray-700">{formatMillionsMKD(f.total_liabilities)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
