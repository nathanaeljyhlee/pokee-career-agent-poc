"use client";

interface Props {
  title: string;
  subtitle?: string;
  score: number;
  rationale: string;
  tags: string[];
  badges?: { label: string; color: string }[];
  meta?: { label: string; value: string }[];
  children?: React.ReactNode;
}

export function RecommendationCard({ title, subtitle, score, rationale, tags, badges, meta, children }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900">{title}</h4>
          {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
        </div>
        <div className="ml-3 flex-shrink-0 w-12 h-12 rounded-full border-2 border-[#006747] flex items-center justify-center">
          <span className="text-sm font-bold text-[#006747]">{Math.round(score)}</span>
        </div>
      </div>

      {badges && badges.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {badges.map((b) => (
            <span key={b.label} className={`px-2 py-0.5 rounded-full text-xs font-medium ${b.color}`}>
              {b.label}
            </span>
          ))}
        </div>
      )}

      <p className="text-sm text-gray-600 mb-3">{rationale}</p>

      {meta && meta.length > 0 && (
        <div className="flex flex-wrap gap-x-4 gap-y-1 mb-3 text-xs text-gray-500">
          {meta.map((m) => (
            <span key={m.label}>
              <span className="font-medium">{m.label}:</span> {m.value}
            </span>
          ))}
        </div>
      )}

      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {tags.slice(0, 6).map((t) => (
            <span key={t} className="px-2 py-0.5 bg-[#006747]/10 text-[#006747] text-xs rounded-full">
              {t}
            </span>
          ))}
          {tags.length > 6 && (
            <span className="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs rounded-full">
              +{tags.length - 6} more
            </span>
          )}
        </div>
      )}

      {children}
    </div>
  );
}
