"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getProjectRecommendations, type ProjectRec } from "@/lib/api";
import { getSessionId } from "@/lib/session";
import { RecommendationCard } from "@/components/RecommendationCard";

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: "bg-green-100 text-green-700",
  intermediate: "bg-yellow-100 text-yellow-700",
  advanced: "bg-red-100 text-red-700",
};

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectRec[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const sid = getSessionId();
    if (!sid) {
      setError("No session found. Please analyze your profile first.");
      setLoading(false);
      return;
    }
    getProjectRecommendations(sid)
      .then((res) => setProjects(res.recommendations))
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Recommended Projects</h1>
        <p className="text-gray-500">Hands-on projects to build skills and strengthen your portfolio</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {projects.map((p) => (
          <RecommendationCard
            key={p.title}
            title={p.title}
            subtitle={p.project_type.charAt(0).toUpperCase() + p.project_type.slice(1)}
            score={p.relevance_score}
            rationale={p.rationale}
            tags={p.skills_developed}
            badges={[
              { label: p.difficulty, color: DIFFICULTY_COLORS[p.difficulty] || "bg-gray-100 text-gray-600" },
            ]}
            meta={[
              { label: "Hours", value: String(p.estimated_hours) },
              { label: "Gaps Addressed", value: String(p.gaps_addressed.length) },
            ]}
          >
            <p className="text-sm text-gray-500 mt-3">{p.description}</p>
          </RecommendationCard>
        ))}
      </div>

      {projects.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No project recommendations yet. Complete your profile analysis first.</p>
        </div>
      )}
    </div>
  );
}
