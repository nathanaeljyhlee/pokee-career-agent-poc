"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import type { SchoolComparison as SC } from "@/lib/api";

interface Props {
  data: SC[];
}

export function SchoolComparison({ data }: Props) {
  const salaryData = data.map((school) => {
    const avgSalary =
      school.outcomes_by_industry.reduce((sum, o) => sum + (o.avg_salary || 0), 0) /
      (school.outcomes_by_industry.filter((o) => o.avg_salary).length || 1);

    const avgEmp =
      school.outcomes_by_industry.reduce((sum, o) => sum + (o.employment_rate || 0), 0) /
      (school.outcomes_by_industry.filter((o) => o.employment_rate).length || 1);

    return {
      school: school.school,
      "Avg Salary ($K)": Math.round(avgSalary / 1000),
      "Employment Rate (%)": Math.round(avgEmp),
    };
  });

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="font-semibold text-gray-900 mb-4">School Comparison</h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={salaryData} margin={{ top: 5, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="school" angle={-35} textAnchor="end" tick={{ fontSize: 11 }} height={80} />
          <YAxis yAxisId="salary" orientation="left" tick={{ fontSize: 11 }} />
          <YAxis yAxisId="emp" orientation="right" domain={[0, 100]} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Legend />
          <Bar yAxisId="salary" dataKey="Avg Salary ($K)" fill="#006747" radius={[4, 4, 0, 0]} />
          <Bar yAxisId="emp" dataKey="Employment Rate (%)" fill="#66bb6a" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
