import TickerList from '../components/ticker/TickerList';

export default function HomePage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Macedonian Stock Exchange</h1>
        <p className="text-gray-500">AI-powered equity research for MSE-listed companies</p>
      </div>
      <div>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
          Popular Tickers
        </h2>
        <TickerList />
      </div>
    </div>
  );
}
