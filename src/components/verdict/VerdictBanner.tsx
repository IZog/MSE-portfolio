import type { Verdict } from '../../types';

interface Props {
  verdict: Verdict;
}

function ratingStyle(rating: string): { bg: string; text: string } {
  const lower = rating.toLowerCase();
  if (lower.includes('strong buy')) return { bg: 'bg-green-800', text: 'text-white' };
  if (lower.includes('buy')) return { bg: 'bg-green-600', text: 'text-white' };
  if (lower.includes('hold')) return { bg: 'bg-amber-500', text: 'text-white' };
  if (lower.includes('avoid') || lower.includes('sell')) return { bg: 'bg-red-600', text: 'text-white' };
  return { bg: 'bg-gray-600', text: 'text-white' };
}

export default function VerdictBanner({ verdict }: Props) {
  const style = ratingStyle(verdict.rating);

  return (
    <div className={`${style.bg} ${style.text} rounded-lg p-6 shadow-sm`}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <div className="text-sm font-medium opacity-80 uppercase tracking-wide mb-1">Research Verdict</div>
          <div className="text-3xl font-bold">{verdict.rating}</div>
        </div>
        <div className="text-right">
          <div className="text-sm font-medium opacity-80 mb-1">Score</div>
          <div className="text-4xl font-bold">{verdict.total_score}<span className="text-lg opacity-70">/100</span></div>
        </div>
      </div>
      <p className="mt-4 text-sm leading-relaxed opacity-90">{verdict.summary}</p>
    </div>
  );
}
