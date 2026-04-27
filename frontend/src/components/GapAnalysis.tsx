"use client";

import type { CareerGap } from "@/lib/api";

interface Props {
  gaps: CareerGap[];
}

const FIT_COLORS: Record<string, string> = {
  "Strong Fit": "bg-green-100 text-green-800 border-green-200",
  "Good Fit": "bg-blue-100 text-blue-800 border-blue-200",
  Developing: "bg-yellow-100 text-yellow-800 border-yellow-200",
  "Needs Development": "bg-red-100 text-red-800 border-red-200",
};

export function GapAnalysis({ gaps }: Props) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="font-semibold text-gray-900 mb-4">Career Path Gap Analysis</h3>
      <div className="space-y-4">
        {gaps.map((gap) => (
          <div key={gap.career_path} className="border border-gray-100 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h4 className="font-medium text-gray-900">{gap.career_path}</h4>
                <p className="text-xs text-gray-500">{gap.industry}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-2 py-1 rounded-full text-xs font-medium border ${FIT_COLORS[gap.fit_level] || ""}`}>
                  {gap.fit_level}
                </span>
                <span className="text-lg font-bold text-[#006747]">{gap.combined_match_score ?? gap.match_percentage}%</span>
              </div>
            </div>

            <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
              <div
                className="h-2 rounded-full bg-[#006747] transition-all"
                style={{ width: `${Math.min(gap.combined_match_score ?? gap.match_percentage, 100)}%` }}
              />
            </div>

            {gap.semantic_match_score !== undefined && (
              <p className="text-xs text-gray-400 mb-3">
                Semantic match {gap.semantic_match_score}% · rule match {gap.match_percentage}%
              </p>
            )}

            {gap.matching_skills.length > 0 && (
              <div className="mb-2">
                <p className="text-xs font-medium text-green-700 mb-1">Skills you have:</p>
                <div className="flex flex-wrap gap-1">
                  {gap.matching_skills.map((s) => (
                    <span key={s} className="px-2 py-0.5 bg-green-50 text-green-700 text-xs rounded-full">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {gap.missing_essential_skills.length > 0 && (
              <div>
                <p className="text-xs font-medium text-red-700 mb-1">Essential skills to develop:</p>
                <div className="flex flex-wrap gap-1">
                  {(gap.priority_missing_skills || gap.missing_essential_skills).map((s) => (
                    <span key={s} className="px-2 py-0.5 bg-red-50 text-red-700 text-xs rounded-full">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
