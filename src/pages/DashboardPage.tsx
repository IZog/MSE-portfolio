import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useResearch } from '../hooks/useResearch';
import DashboardLayout from '../components/layout/DashboardLayout';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorDisplay from '../components/common/ErrorDisplay';
import RefreshButton from '../components/common/RefreshButton';
import VerdictBanner from '../components/verdict/VerdictBanner';
import SummaryReport from '../components/verdict/SummaryReport';
import CompanyProfile from '../components/profile/CompanyProfile';
import PriceCard from '../components/price/PriceCard';
import PriceChart from '../components/price/PriceChart';
import VolumeChart from '../components/price/VolumeChart';
import FinancialsTable from '../components/financials/FinancialsTable';
import RatiosTable from '../components/financials/RatiosTable';
import ValuationCard from '../components/analysis/ValuationCard';
import TechnicalCard from '../components/analysis/TechnicalCard';
import RiskCard from '../components/analysis/RiskCard';
import MacroCard from '../components/analysis/MacroCard';

export default function DashboardPage() {
  const { ticker } = useParams<{ ticker: string }>();
  const { report, loading, error, load } = useResearch();

  useEffect(() => {
    if (ticker) load(ticker);
  }, [ticker, load]);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error} onRetry={() => ticker && load(ticker, true)} />;
  if (!report) return <LoadingSpinner />;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-5">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">{report.ticker}</h1>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">
            Generated: {new Date(report.generated_at).toLocaleString()}
          </span>
          <RefreshButton onClick={() => ticker && load(ticker, true)} loading={loading} />
        </div>
      </div>

      {/* Verdict banner - full width */}
      <VerdictBanner verdict={report.verdict} />

      {/* Main grid */}
      <DashboardLayout>
        {/* Left column */}
        <div className="space-y-5">
          <CompanyProfile company={report.company} />
          <RatiosTable ratios={report.ratios} />
          <MacroCard macro={report.macro} />
        </div>

        {/* Middle column - spans 2 cols on large screens */}
        <div className="lg:col-span-2 space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <PriceCard price={report.price} />
            <ValuationCard valuation={report.valuation} />
          </div>
          <PriceChart history={report.price_history} technical={report.technical} />
          <VolumeChart history={report.price_history} />
          <FinancialsTable financials={report.financials} />
          <SummaryReport verdict={report.verdict} />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <TechnicalCard technical={report.technical} />
            <RiskCard risk={report.risk} />
          </div>
        </div>
      </DashboardLayout>
    </div>
  );
}
