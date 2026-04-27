"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getJobRecommendations, type JobRec } from "@/lib/api";
import { getSessionId } from "@/lib/session";
import { RecommendationCard } from "@/components/RecommendationCard";

function formatSalary(n: number) {
  return `$${(n / 1000).toFixed(0)}K`;
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobRec[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const sid = getSessionId();
    if (!sid) {
      setError("No session found. Please analyze your profile first.");
      setLoading(false);
      return;
    }
    getJobRecommendations(sid)
      .then((res) => setJobs(res.recommendations))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-10 h-10 border-4 border-[#006747] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <Link href="/dashboard" className="text-[#006747] hover:underline">Go to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Job Matches</h1>
        <p className="text-gray-500">MBA-level positions matched to your skill profile</p>
      </div>

      <div className="space-y-4">
        {jobs.map((j) => (
          <RecommendationCard
            key={j.title}
            title={j.title}
            subtitle={`${j.company_type} | ${j.industry} | ${j.location}`}
            score={j.relevance_score}
            rationale={j.rationale}
            tags={j.matching_skills}
            badges={[
              {
                label: `${formatSalary(j.salary_range.min)}-${formatSalary(j.salary_range.max)}`,
                color: "bg-green-100 text-green-700",
              },
              { label: `${j.required_match_pct}% match`, color: "bg-blue-100 text-blue-700" },
            ]}
            meta={[
              { label: "Experience", value: j.experience_required },
            ]}
          >
            <div className="mt-3">
              <p className="text-sm text-gray-600 mb-2">{j.description}</p>
              {j.missing_required_skills.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-red-600 mb-1">Skills to develop:</p>
                  <div className="flex flex-wrap gap-1">
                    {j.missing_required_skills.map((s) => (
                      <span key={s} className="px-2 py-0.5 bg-red-50 text-red-600 text-xs rounded-full">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </RecommendationCard>
        ))}
      </div>

      {jobs.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No job matches yet. Complete your profile analysis first.</p>
        </div>
      )}
    </div>
  );
}
