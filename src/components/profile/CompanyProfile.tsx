import type { CompanyProfile as CompanyProfileType } from '../../types';
import Card from '../common/Card';

interface Props {
  company: CompanyProfileType;
}

export default function CompanyProfile({ company }: Props) {
  return (
    <Card title="Company Profile">
      <h2 className="text-xl font-bold text-gray-900 mb-1">{company.name}</h2>
      {company.sector && (
        <span className="inline-block text-xs font-medium bg-blue-100 text-blue-700 px-2 py-0.5 rounded mb-3">
          {company.sector}
        </span>
      )}
      {company.description && (
        <p className="text-sm text-gray-600 mb-4 leading-relaxed">{company.description}</p>
      )}
      <dl className="space-y-2 text-sm">
        {company.address && (
          <div className="flex justify-between">
            <dt className="text-gray-500">Address</dt>
            <dd className="text-gray-900 text-right max-w-[60%]">{company.address}</dd>
          </div>
        )}
      </dl>
    </Card>
  );
}
