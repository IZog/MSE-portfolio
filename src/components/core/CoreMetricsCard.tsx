import type { PriceData, TechnicalAnalysis, ValuationMetrics, FinancialRatios } from '../../types';
import { formatMKD, formatPercent, formatRatio, formatMillionsMKD } from '../../utils/format';

interface Props {
  price: PriceData;
  technical: TechnicalAnalysis;
  valuation: ValuationMetrics;
  ratios: FinancialRatios;
}

function MetricBox({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="text-center px-3 py-2">
      <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</div>
      <div className="text-lg font-bold text-gray-900">{value}</div>
      {sub && <div className="text-xs text-gray-400 mt-0.5">{sub}</div>}
    </div>
  );
}

export default function CoreMetricsCard({ price, technical, valuation, ratios }: Props) {
  const ytdColor = technical.ytd_return_pct != null && technical.ytd_return_pct >= 0 ? 'text-green-600' : 'text-red-600';

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100">
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 divide-x divide-gray-100">
        <MetricBox
          label="Price"
          value={price.current_price != null ? formatMKD(price.current_price) : 'N/A'}
        />
        <MetricBox
          label="Market Cap"
          value={price.market_cap != null ? formatMillionsMKD(price.market_cap) : 'N/A'}
        />
        <MetricBox
          label="P/E"
          value={valuation.pe_ratio != null ? formatRatio(valuation.pe_ratio) : 'N/A'}
          sub={valuation.pe_assessment ?? undefined}
        />
        <MetricBox
          label="Div. Yield"
          value={valuation.dividend_yield != null ? formatPercent(valuation.dividend_yield) : 'N/A'}
          sub={ratios.dividend_per_share != null ? `DPS: ${formatRatio(ratios.dividend_per_share)} MKD` : undefined}
        />
        <MetricBox
          label="EPS"
          value={ratios.eps != null ? `${formatRatio(ratios.eps)} MKD` : 'N/A'}
        />
        <div className="text-center px-3 py-2">
          <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">YTD Return</div>
          <div className={`text-lg font-bold ${technical.ytd_return_pct != null ? ytdColor : 'text-gray-900'}`}>
            {technical.ytd_return_pct != null ? formatPercent(technical.ytd_return_pct) : 'N/A'}
          </div>
        </div>
      </div>
    </div>
  );
}
