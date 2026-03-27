import type { DisclosureInfo, DividendRecord } from '../../types';
import Card from '../common/Card';

interface Props {
  disclosures: DisclosureInfo | null;
  dividendHistory?: DividendRecord[];
}

export default function DisclosuresCard({ disclosures, dividendHistory }: Props) {
  if (!disclosures) {
    return (
      <Card title="Disclosures & News">
        <p className="text-sm text-gray-400">No disclosure data available.</p>
      </Card>
    );
  }

  return (
    <Card title="Disclosures & News">
      <div className="space-y-4">
        {/* Summary row */}
        <dl className="space-y-2 text-sm">
          {disclosures.last_seinet_date && (
            <div className="flex justify-between">
              <dt className="text-gray-500">Latest SEINET</dt>
              <dd className="text-gray-900 font-medium">{disclosures.last_seinet_date}</dd>
            </div>
          )}
          {disclosures.last_report_date && (
            <div className="flex justify-between">
              <dt className="text-gray-500">Last Financial Report</dt>
              <dd className="text-gray-900 font-medium">{disclosures.last_report_date}</dd>
            </div>
          )}
          {disclosures.last_dividend_date && (
            <div className="flex justify-between">
              <dt className="text-gray-500">Last Dividend</dt>
              <dd className="text-gray-900 font-medium">
                {disclosures.last_dividend_date}
                {disclosures.last_dividend_amount != null && (
                  <span className="text-gray-500 ml-1">({disclosures.last_dividend_amount.toLocaleString()} MKD)</span>
                )}
              </dd>
            </div>
          )}
        </dl>

        {/* Dividend history table */}
        {dividendHistory && dividendHistory.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Dividend History</h4>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-1 text-gray-500 font-medium">Year</th>
                  <th className="text-right py-1 text-gray-500 font-medium">DPS (MKD)</th>
                  <th className="text-right py-1 text-gray-500 font-medium">Yield</th>
                </tr>
              </thead>
              <tbody>
                {dividendHistory.map((d) => (
                  <tr key={d.year} className="border-b border-gray-50">
                    <td className="py-1 text-gray-700">{d.year}</td>
                    <td className="py-1 text-right text-gray-900 font-medium">
                      {d.dps != null ? d.dps.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '—'}
                    </td>
                    <td className="py-1 text-right text-gray-600">
                      {d.yield_pct != null ? `${d.yield_pct.toFixed(2)}%` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Recent news */}
        {disclosures.recent_news.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">Recent News</h4>
            <ul className="space-y-2">
              {disclosures.recent_news.slice(0, 5).map((item, i) => (
                <li key={i} className="text-sm border-l-2 border-blue-200 pl-3">
                  {item.date && (
                    <span className="text-xs text-gray-400 block">{item.date}</span>
                  )}
                  {item.url ? (
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 hover:underline"
                    >
                      {item.title ?? 'Untitled'}
                    </a>
                  ) : (
                    <span className="text-gray-700">{item.title ?? 'Untitled'}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {disclosures.recent_news.length === 0 && !disclosures.last_seinet_date && (
          <p className="text-sm text-gray-400">No recent disclosures found on MSE.</p>
        )}
      </div>
    </Card>
  );
}
