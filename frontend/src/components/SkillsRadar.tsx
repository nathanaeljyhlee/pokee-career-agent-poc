"use client";

import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { CareerGap } from "@/lib/api";

interface Props {
  gaps: CareerGap[];
}

export function SkillsRadar({ gaps }: Props) {
  const top5 = gaps.slice(0, 5);
  const data = top5.map((g) => ({
    path: g.career_path.replace(/ (Associate|Manager|Consultant|Scientist)/, ""),
    match: Math.round(g.match_percentage),
    full: 100,
  }));

  if (data.length === 0) {
    return <p className="text-gray-500 text-center py-8">No career gap data available.</p>;
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="font-semibold text-gray-900 mb-4">Career Fit Radar</h3>
      <ResponsiveContainer width="100%" height={350}>
        <RadarChart data={data}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis dataKey="path" tick={{ fontSize: 11, fill: "#6b7280" }} />
          <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 10 }} />
          <Radar name="Your Match %" dataKey="match" stroke="#006747" fill="#006747" fillOpacity={0.3} />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
