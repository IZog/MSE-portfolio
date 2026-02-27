import type { Verdict } from '../../types';
import Card from '../common/Card';

interface Props {
  verdict: Verdict;
}

export default function SummaryReport({ verdict }: Props) {
  return (
    <Card title="Key Takeaways">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-sm font-semibold text-green-700 mb-2">Positives</h4>
          <ul className="space-y-1.5">
            {verdict.key_positives.map((p, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-green-500 mt-0.5 flex-shrink-0">&#9679;</span>
                {p}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold text-red-700 mb-2">Negatives</h4>
          <ul className="space-y-1.5">
            {verdict.key_negatives.map((n, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-red-500 mt-0.5 flex-shrink-0">&#9679;</span>
                {n}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Card>
  );
}
