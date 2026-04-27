"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { analyzeProfile, type Analysis } from "@/lib/api";
import { getSessionId } from "@/lib/session";
import { SkillsRadar } from "@/components/SkillsRadar";
import { GapAnalysis } from "@/components/GapAnalysis";
import { SkillsHeatmap } from "@/components/SkillsHeatmap";

export default function DashboardPage() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const sid = getSessionId();
    if (!sid) {
      setError("No session found. Please upload your documents first.");
      setLoading(false);
      return;
    }

    analyzeProfile(sid)
      .then((res) => setAnalysis(res.analysis))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-[#006747] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Analyzing your profile...</p>
          <p className="text-sm text-gray-400 mt-1">This may take a moment</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center">
        <div className="bg-red-50 border border-red-200 rounded-xl p-8">
          <h2 className="text-xl font-semibold text-red-800 mb-2">Unable to Analyze</h2>
          <p className="text-red-600 mb-4">{error}</p>
          <Link href="/upload" className="px-6 py-2 bg-[#006747] text-white rounded-lg hover:bg-[#004d35]">
            Upload Documents
          </Link>
        </div>
      </div>
    );
  }

  if (!analysis) return null;

  const ent = analysis.entrepreneurship_readiness;
  const insights = analysis.ai_insights;
  const advisor = analysis.local_advisor;
  const transcript = analysis.transcript_summary;
  const intelligence = analysis.intelligence;
  const evidence = analysis.skill_evidence || [];

  const providerLabel =
    !intelligence ? "Deterministic analysis" :
    intelligence.provider === "ollama" ? "Offline local AI" :
    intelligence.provider === "azure" ? "Online Azure AI" :
    "Fallback mode";

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Career Dashboard</h1>
            <p className="text-gray-500">
              {analysis.total_skills_identified} skills identified across your profile
            </p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm shadow-sm md:min-w-56">
            <div className="font-medium text-gray-900">{providerLabel}</div>
            <div className="mt-1 text-xs text-gray-500">
              {intelligence?.model || "Rules-based scoring"}
              {intelligence?.fallback_used ? " · fallback active" : ""}
            </div>
            {analysis.performance && (
              <div className="mt-2 text-xs text-gray-400">
                Analyze {analysis.performance.extraction_ms + analysis.performance.scoring_ms + analysis.performance.embedding_ms + analysis.performance.advisor_ms}ms
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Top cards */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {/* Entrepreneurship Score */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-3">Entrepreneurship Readiness</h3>
          <div className="flex items-end gap-3 mb-3">
            <span className="text-4xl font-bold text-[#006747]">{ent.score}</span>
            <span className="text-lg text-gray-400 mb-1">/ {ent.out_of}</span>
          </div>
          <p className="text-sm text-gray-600 mb-3">{ent.interpretation}</p>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="h-2 rounded-full bg-[#006747]" style={{ width: `${ent.score}%` }} />
          </div>
          <p className="text-xs text-gray-400 mt-2">
            {ent.entrepreneurship_skills_count} of {ent.skills_present.length + ent.skills_missing.length} entrepreneurship skills
          </p>
        </div>

        {/* Experience Summary */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-3">Experience Summary</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Roles</span>
              <span className="font-semibold">{analysis.experience_summary.total_roles}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Years Experience</span>
              <span className="font-semibold">{analysis.experience_summary.estimated_years_experience || "N/A"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Skills Identified</span>
              <span className="font-semibold">{analysis.total_skills_identified}</span>
            </div>
          </div>
        </div>

        {/* Transcript (if available) */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-sm font-medium text-gray-500 mb-3">Academic Profile</h3>
          {transcript ? (
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">GPA</span>
                <span className="font-semibold">{transcript.gpa || "N/A"}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Credits</span>
                <span className="font-semibold">{transcript.credits_completed} / {transcript.credits_required}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Courses</span>
                <span className="font-semibold">{transcript.total_courses}</span>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-sm text-gray-400 mb-2">No transcript connected</p>
              <Link href="/transcript" className="text-sm text-[#006747] hover:underline">
                Connect Workday
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Local Advisor */}
      {advisor && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-2">Local Advisor</h3>
          <p className="text-sm text-gray-600 mb-4">{advisor.summary}</p>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h4 className="text-sm font-medium text-green-700 mb-2">Strengths</h4>
              <ul className="space-y-1">
                {advisor.strengths.map((s, i) => (
                  <li key={i} className="text-sm text-gray-600">{s}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-medium text-amber-700 mb-2">Development Areas</h4>
              <ul className="space-y-1">
                {advisor.development_areas.map((s, i) => (
                  <li key={i} className="text-sm text-gray-600">{s}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-medium text-blue-700 mb-2">Next Steps</h4>
              <ul className="space-y-1">
                {advisor.recommended_next_steps.map((s, i) => (
                  <li key={i} className="text-sm text-gray-600">{s}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {!advisor && insights && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-4">AI Insights</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-medium text-green-700 mb-2">Strengths</h4>
              <ul className="space-y-1">
                {insights.strengths.map((s, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-green-500 mt-0.5">+</span> {s}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-medium text-amber-700 mb-2">Development Areas</h4>
              <ul className="space-y-1">
                {insights.development_areas.map((s, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-amber-500 mt-0.5">!</span> {s}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-medium text-blue-700 mb-2">Career Recommendations</h4>
              <ul className="space-y-1">
                {insights.career_recommendations.map((s, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-blue-500 mt-0.5">&#8594;</span> {s}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-medium text-purple-700 mb-2">Immediate Actions</h4>
              <ul className="space-y-1">
                {insights.immediate_actions.map((s, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-purple-500 mt-0.5">*</span> {s}
                  </li>
                ))}
              </ul>
            </div>
          </div>
          {insights.entrepreneurship_assessment && (
            <div className="mt-4 p-3 bg-[#006747]/5 rounded-lg">
              <p className="text-sm text-[#006747]">
                <span className="font-medium">Entrepreneurship Assessment:</span>{" "}
                {insights.entrepreneurship_assessment}
              </p>
            </div>
          )}
        </div>
      )}

      {evidence.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-4">Evidence-Backed Skills</h3>
          <div className="grid md:grid-cols-2 gap-3">
            {evidence.slice(0, 12).map((item, i) => (
              <div key={`${item.skill}-${i}`} className="rounded-lg border border-gray-100 p-3">
                <div className="flex items-center justify-between gap-3">
                  <h4 className="text-sm font-medium text-gray-900">{item.skill}</h4>
                  <span className="shrink-0 text-xs text-gray-500">{Math.round(item.confidence * 100)}%</span>
                </div>
                <p className="mt-1 text-xs text-gray-500">{item.source} · {item.evidence_type}</p>
                {item.evidence_text && <p className="mt-2 text-sm text-gray-600">{item.evidence_text}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        <SkillsRadar gaps={analysis.career_gap_analysis} />
        <SkillsHeatmap skillsInventory={analysis.skills_inventory} />
      </div>

      {/* Gap Analysis */}
      <div className="mb-8">
        <GapAnalysis gaps={analysis.career_gap_analysis} />
      </div>

      {/* Quick Links */}
      <div className="grid md:grid-cols-3 gap-4">
        {[
          { href: "/recommendations/courses", label: "View Course Recommendations", color: "bg-blue-50 text-blue-700 hover:bg-blue-100" },
          { href: "/recommendations/projects", label: "View Project Ideas", color: "bg-purple-50 text-purple-700 hover:bg-purple-100" },
          { href: "/recommendations/jobs", label: "View Job Matches", color: "bg-green-50 text-green-700 hover:bg-green-100" },
        ].map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={`p-4 rounded-xl text-center font-medium transition-colors ${link.color}`}
          >
            {link.label}
          </Link>
        ))}
      </div>
    </div>
  );
}
