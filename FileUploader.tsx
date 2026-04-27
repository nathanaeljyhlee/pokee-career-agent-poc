"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getCourseRecommendations, type CourseRec } from "@/lib/api";
import { getSessionId } from "@/lib/session";
import { RecommendationCard } from "@/components/RecommendationCard";

export default function CoursesPage() {
  const [courses, setCourses] = useState<CourseRec[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const sid = getSessionId();
    if (!sid) {
      setError("No session found. Please analyze your profile first.");
      setLoading(false);
      return;
    }
    getCourseRecommendations(sid)
      .then((res) => setCourses(res.recommendations))
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
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Recommended Courses</h1>
        <p className="text-gray-500">Courses that fill your skill gaps and build new competencies</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {courses.map((c) => (
          <RecommendationCard
            key={`${c.course_code}-${c.school}`}
            title={c.name}
            subtitle={`${c.school} ${c.course_code ? `(${c.course_code})` : ""}`}
            score={c.relevance_score}
            rationale={c.rationale}
            tags={c.skills_taught}
            badges={[
              { label: c.is_elective ? "Elective" : "Core", color: c.is_elective ? "bg-blue-100 text-blue-700" : "bg-green-100 text-green-700" },
              ...(c.semester ? [{ label: c.semester, color: "bg-gray-100 text-gray-600" }] : []),
            ]}
            meta={[
              { label: "Credits", value: String(c.credits) },
              { label: "Gaps Addressed", value: String(c.gaps_addressed.length) },
            ]}
          />
        ))}
      </div>

      {courses.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No course recommendations available. Complete your profile analysis first.</p>
        </div>
      )}
    </div>
  );
}
