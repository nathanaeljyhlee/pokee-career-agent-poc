"use client";

import type { Analysis } from "@/lib/api";

interface Props {
  skillsInventory: Analysis["skills_inventory"];
}

const CATEGORY_COLORS: Record<string, string> = {
  technical: "bg-blue-500",
  soft: "bg-purple-500",
  domain: "bg-amber-500",
  entrepreneurship: "bg-emerald-500",
  uncategorized: "bg-gray-400",
};

const CATEGORY_LABELS: Record<string, string> = {
  technical: "Technical Skills",
  soft: "Soft / Leadership",
  domain: "Domain Knowledge",
  entrepreneurship: "Entrepreneurship",
  uncategorized: "Other",
};

export function SkillsHeatmap({ skillsInventory }: Props) {
  const categories = Object.entries(skillsInventory).filter(([, skills]) => skills.length > 0);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="font-semibold text-gray-900 mb-4">Skills Inventory</h3>

      <div className="flex flex-wrap gap-2 mb-6">
        {categories.map(([cat]) => (
          <div key={cat} className="flex items-center gap-1.5">
            <div className={`w-3 h-3 rounded-full ${CATEGORY_COLORS[cat]}`} />
            <span className="text-xs text-gray-600">{CATEGORY_LABELS[cat] || cat}</span>
          </div>
        ))}
      </div>

      <div className="space-y-4">
        {categories.map(([cat, skills]) => (
          <div key={cat}>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-700">{CATEGORY_LABELS[cat] || cat}</h4>
              <span className="text-xs text-gray-400">{skills.length} skills</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {skills.map((s) => (
                <span
                  key={s.name}
                  className={`px-2.5 py-1 rounded-md text-xs text-white font-medium ${CATEGORY_COLORS[cat]}`}
                  title={s.subcategory}
                >
                  {s.name}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
