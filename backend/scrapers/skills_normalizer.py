"""
Skills normalizer — maps varied skill terms from resumes, job postings,
and school curricula to our canonical skills taxonomy.

Uses fuzzy matching and synonym lookup to normalize terms.
"""

import json
import sys
from pathlib import Path
from difflib import SequenceMatcher

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.connection import query


def load_skill_taxonomy() -> dict:
    """Load all canonical skills and their synonyms from the database."""
    skills = query("SELECT id, name, category, subcategory FROM skills")
    synonyms = query("SELECT skill_id, synonym FROM skill_synonyms")

    taxonomy = {}
    for s in skills:
        taxonomy[s["name"].lower()] = {
            "id": s["id"],
            "canonical_name": s["name"],
            "category": s["category"],
            "subcategory": s["subcategory"],
        }

    synonym_map = {}
    for syn in synonyms:
        skill = next((s for s in skills if s["id"] == syn["skill_id"]), None)
        if skill:
            synonym_map[syn["synonym"].lower()] = {
                "id": skill["id"],
                "canonical_name": skill["name"],
                "category": skill["category"],
            }

    return taxonomy, synonym_map


def normalize_skill(raw_skill: str, taxonomy: dict = None, synonym_map: dict = None) -> dict | None:
    """
    Normalize a raw skill string to a canonical skill.
    Returns None if no match found above threshold.
    """
    if taxonomy is None or synonym_map is None:
        taxonomy, synonym_map = load_skill_taxonomy()

    raw_lower = raw_skill.strip().lower()

    # Exact match on canonical name
    if raw_lower in taxonomy:
        return taxonomy[raw_lower]

    # Exact match on synonym
    if raw_lower in synonym_map:
        return synonym_map[raw_lower]

    # Fuzzy matching against canonical names
    best_match = None
    best_score = 0.0
    threshold = 0.75

    for canonical_lower, info in taxonomy.items():
        score = SequenceMatcher(None, raw_lower, canonical_lower).ratio()
        if score > best_score and score >= threshold:
            best_score = score
            best_match = {**info, "match_score": score}

    # Fuzzy matching against synonyms
    for syn_lower, info in synonym_map.items():
        score = SequenceMatcher(None, raw_lower, syn_lower).ratio()
        if score > best_score and score >= threshold:
            best_score = score
            best_match = {**info, "match_score": score}

    return best_match


def normalize_skill_list(raw_skills: list) -> list:
    """Normalize a list of raw skill strings."""
    taxonomy, synonym_map = load_skill_taxonomy()
    results = []
    for raw in raw_skills:
        match = normalize_skill(raw, taxonomy, synonym_map)
        results.append({
            "raw": raw,
            "normalized": match,
            "matched": match is not None,
        })
    return results


def get_skill_gaps(student_skills: list, target_role_skills: list) -> dict:
    """
    Compare student's skills against a target role's requirements.
    Returns skills the student has, skills they're missing, and overlap.
    """
    taxonomy, synonym_map = load_skill_taxonomy()

    student_normalized = set()
    for skill in student_skills:
        match = normalize_skill(skill, taxonomy, synonym_map)
        if match:
            student_normalized.add(match["canonical_name"])

    target_normalized = set()
    for skill in target_role_skills:
        match = normalize_skill(skill, taxonomy, synonym_map)
        if match:
            target_normalized.add(match["canonical_name"])

    overlap = student_normalized & target_normalized
    missing = target_normalized - student_normalized
    extra = student_normalized - target_normalized

    return {
        "matching_skills": sorted(overlap),
        "missing_skills": sorted(missing),
        "additional_skills": sorted(extra),
        "match_percentage": len(overlap) / len(target_normalized) * 100 if target_normalized else 0,
        "total_student_skills": len(student_normalized),
        "total_target_skills": len(target_normalized),
    }


COMMON_RESUME_VARIATIONS = {
    "python": "Python Programming",
    "sql": "SQL & Database Management",
    "excel": "Excel / Google Sheets (Advanced)",
    "powerpoint": "Presentation Design",
    "tableau": "Tableau / Power BI",
    "power bi": "Tableau / Power BI",
    "financial analysis": "Financial Modeling",
    "leadership": "Team Leadership",
    "communication": "Communication (Verbal)",
    "public speaking": "Public Speaking",
    "data analysis": "Statistical Analysis",
    "project management": "Project Management Tools",
    "scrum": "Agile / Scrum Methodology",
    "agile": "Agile / Scrum Methodology",
    "salesforce": "CRM Systems (Salesforce)",
    "sap": "ERP Systems (SAP)",
    "r": "R Programming",
    "machine learning": "Machine Learning Fundamentals",
    "deep learning": "Machine Learning Fundamentals",
    "nlp": "Natural Language Processing",
    "aws": "Cloud Computing (AWS/Azure/GCP)",
    "azure": "Cloud Computing (AWS/Azure/GCP)",
    "gcp": "Cloud Computing (AWS/Azure/GCP)",
    "html": "Web Development",
    "css": "Web Development",
    "javascript": "Web Development",
    "react": "Web Development",
    "ux": "UX/UI Design Principles",
    "ui": "UX/UI Design Principles",
    "google analytics": "Digital Marketing Analytics",
    "seo": "SEO / SEM",
    "sem": "SEO / SEM",
    "a/b testing": "A/B Testing & Experimentation",
    "six sigma": "Quality Management (Six Sigma)",
    "lean": "Lean Startup Methodology",
    "dcf": "Valuation Methods",
    "m&a": "Mergers & Acquisitions Analysis",
    "fundraising": "Fundraising Strategy",
    "business development": "Business Development",
    "strategy": "Strategic Thinking",
    "operations": "Operations Strategy",
    "supply chain": "Supply Chain Management",
    "marketing": "Marketing Strategy",
    "sales": "Sales Strategy",
    "consulting": "Management Consulting Frameworks",
    "venture capital": "Venture Capital",
    "private equity": "Private Equity",
    "blockchain": "Blockchain Fundamentals",
    "cybersecurity": "Cybersecurity Basics",
    "negotiation": "Negotiation",
    "teamwork": "Cross-functional Collaboration",
    "problem solving": "Problem Solving",
    "critical thinking": "Critical Thinking",
    "analytics": "Statistical Analysis",
    "data science": "Machine Learning Fundamentals",
    "product management": "Technology Product Management",
    "crm": "CRM Systems (Salesforce)",
    "erp": "ERP Systems (SAP)",
    "jira": "Project Management Tools",
    "asana": "Project Management Tools",
}


def quick_normalize(raw_skill: str) -> str | None:
    """Fast normalization using common resume variations."""
    return COMMON_RESUME_VARIATIONS.get(raw_skill.strip().lower())


if __name__ == "__main__":
    test_skills = [
        "Python", "SQL", "Excel", "Leadership", "Financial Analysis",
        "Machine Learning", "Agile", "Public Speaking", "DCF",
        "Supply Chain", "Unknown Skill XYZ",
    ]
    print("Testing skill normalization:")
    results = normalize_skill_list(test_skills)
    for r in results:
        status = f"-> {r['normalized']['canonical_name']}" if r["matched"] else "-> NOT MATCHED"
        print(f"  {r['raw']:30s} {status}")
