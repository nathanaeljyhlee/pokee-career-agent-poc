"use client";

import { useEffect, useState } from "react";
import { compareSchools, getSchools, getSchoolOutcomes, type School, type SchoolComparison as SC, type Outcome } from "@/lib/api";
import { SchoolComparison } from "@/components/SchoolComparison";

export default function ExplorePage() {
  const [schools, setSchools] = useState<School[]>([]);
  const [comparison, setComparison] = useState<SC[]>([]);
  const [selectedSchool, setSelectedSchool] = useState<string>("");
  const [outcomes, setOutcomes] = useState<Outcome[]>([]);
  const [loadingOutcomes, setLoadingOutcomes] = useState(false);

  useEffect(() => {
    getSchools().then((res) => setSchools(res.schools));
    compareSchools().then((res) => setComparison(res.comparison));
  }, []);

  const handleSchoolSelect = async (shortName: string) => {
    setSelectedSchool(shortName);
    if (!shortName) {
      setOutcomes([]);
      return;
    }
    setLoadingOutcomes(true);
    try {
      const res = await getSchoolOutcomes(shortName);
      setOutcomes(res.outcomes);
    } catch {
      setOutcomes([]);
    } finally {
      setLoadingOutcomes(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Explore MBA Data</h1>
        <p className="text-gray-500">
          Compare job outcomes, salaries, and employment rates across 10 Boston-area MBA programs
        </p>
      </div>

      {/* School Comparison Chart */}
      {comparison.length > 0 && <SchoolComparison data={comparison} />}

      {/* School Selector */}
      <div className="mt-8 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="font-semibold text-gray-900 mb-4">School Details</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mb-6">
          {schools.map((s) => (
            <button
              key={s.short_name}
              onClick={() => handleSchoolSelect(s.short_name)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedSchool === s.short_name
                  ? "bg-[#006747] text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {s.short_name}
            </button>
          ))}
        </div>

        {loadingOutcomes && (
          <div className="flex justify-center py-8">
            <div className="w-8 h-8 border-4 border-[#006747] border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {selectedSchool && outcomes.length > 0 && !loadingOutcomes && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-2 font-medium text-gray-500">Industry</th>
                  <th className="text-left py-3 px-2 font-medium text-gray-500">Function</th>
                  <th className="text-left py-3 px-2 font-medium text-gray-500">Title</th>
                  <th className="text-left py-3 px-2 font-medium text-gray-500">Company</th>
                  <th className="text-right py-3 px-2 font-medium text-gray-500">Median Salary</th>
                  <th className="text-right py-3 px-2 font-medium text-gray-500">Emp. Rate (6mo)</th>
                  <th className="text-right py-3 px-2 font-medium text-gray-500">% of Class</th>
                </tr>
              </thead>
              <tbody>
                {outcomes.map((o, i) => (
                  <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 px-2">{o.industry}</td>
                    <td className="py-2 px-2">{o.job_function || "-"}</td>
                    <td className="py-2 px-2">{o.job_title || "-"}</td>
                    <td className="py-2 px-2">{o.company || "-"}</td>
                    <td className="py-2 px-2 text-right font-medium">
                      {o.median_salary ? `$${(o.median_salary / 1000).toFixed(0)}K` : "-"}
                    </td>
                    <td className="py-2 px-2 text-right">
                      {o.employment_rate_6mo ? `${(o.employment_rate_6mo * 100).toFixed(0)}%` : "-"}
                    </td>
                    <td className="py-2 px-2 text-right">
                      {o.pct_of_class ? `${(o.pct_of_class * 100).toFixed(0)}%` : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {selectedSchool && outcomes.length === 0 && !loadingOutcomes && (
          <p className="text-center py-8 text-gray-400">No outcome data available for this school.</p>
        )}

        {!selectedSchool && (
          <p className="text-center py-8 text-gray-400">Select a school above to view detailed outcomes.</p>
        )}
      </div>

      {/* School Cards */}
      <div className="mt-8 grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {schools.map((s) => (
          <div key={s.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <h4 className="font-semibold text-gray-900">{s.name}</h4>
            <p className="text-sm text-gray-500 mb-3">{s.location}</p>
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="px-2 py-1 bg-gray-100 rounded-full">
                US News: #{s.ranking_us_news || "N/A"}
              </span>
              {s.ranking_entrepreneurship && (
                <span className="px-2 py-1 bg-[#006747]/10 text-[#006747] rounded-full">
                  Entrepreneurship: #{s.ranking_entrepreneurship}
                </span>
              )}
              <span className={`px-2 py-1 rounded-full ${
                s.school_type === "entrepreneurship" ? "bg-green-100 text-green-700" :
                s.school_type === "hybrid" ? "bg-blue-100 text-blue-700" :
                "bg-gray-100 text-gray-600"
              }`}>
                {s.school_type}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
