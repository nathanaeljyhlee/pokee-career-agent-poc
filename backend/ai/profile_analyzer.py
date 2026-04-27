"""
AI-powered profile analyzer — combines resume, LinkedIn, and transcript data
to produce a comprehensive student profile analysis.

Uses Claude for intelligent analysis when API key is available,
falls back to rule-based analysis otherwise.
"""

import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.connection import execute, query
from ai.intelligence import cache_embedding, get_cached_embedding, get_intelligence_provider
from scrapers.skills_normalizer import quick_normalize


def analyze_profile(resume_data: dict = None, linkedin_data: dict = None, transcript_data: dict = None, session_id: str = None) -> dict:
    """
    Analyze a student's combined profile and return:
    - Skills inventory (categorized)
    - Skill gaps vs. common MBA career paths
    - Entrepreneurship readiness score
    - Strengths and development areas
    - Career path suggestions
    """
    timings = {"extraction_ms": 0, "embedding_ms": 0, "scoring_ms": 0, "advisor_ms": 0, "cached_embeddings_used": 0}
    provider = get_intelligence_provider()
    provider_health = provider.health()
    provider_available = provider_health.status == "ok"
    fallback_used = not provider_available

    extraction_start = time.perf_counter()

    # Collect all raw skills from all sources
    raw_skills = set()
    skill_evidence = []

    if resume_data:
        raw_skills.update(resume_data.get("skills", []))
        skill_evidence.extend(resume_data.get("skill_evidence", []))
        for exp in resume_data.get("experience", []):
            for achievement in exp.get("key_achievements", []):
                _extract_implicit_skills(achievement, raw_skills)

    if linkedin_data:
        raw_skills.update(linkedin_data.get("skills", []))
        skill_evidence.extend(linkedin_data.get("skill_evidence", []))

    if transcript_data:
        for course in transcript_data.get("courses", []):
            raw_skills.update(course.get("skills_covered", []))
            for skill in course.get("skills_covered", []):
                skill_evidence.append({
                    "skill": skill,
                    "evidence_text": course.get("name") or course.get("course_name") or course.get("code", ""),
                    "source": "transcript",
                    "confidence": 0.85,
                    "evidence_type": "course_mapped",
                })

    if provider_available:
        try:
            skill_evidence.extend(_extract_missing_local_evidence(provider, "resume", resume_data))
            skill_evidence.extend(_extract_missing_local_evidence(provider, "linkedin", linkedin_data))
        except Exception:
            fallback_used = True

    for item in skill_evidence:
        if item.get("confidence", 0) >= 0.55 and item.get("skill"):
            raw_skills.add(item["skill"])

    timings["extraction_ms"] = round((time.perf_counter() - extraction_start) * 1000)

    # Normalize skills
    normalized = []
    for raw in raw_skills:
        quick = quick_normalize(raw)
        if quick:
            normalized.append({"raw": raw, "canonical": quick, "source": "quick_match"})
        else:
            normalized.append({"raw": raw, "canonical": raw, "source": "direct"})

    # Get canonical skill names
    student_skill_names = list({n["canonical"] for n in normalized})

    # Calculate entrepreneurship readiness
    ent_score = _calculate_entrepreneurship_score(student_skill_names, transcript_data)

    scoring_start = time.perf_counter()

    # Get skill gaps for common paths
    career_gaps = _analyze_career_gaps(student_skill_names)
    timings["scoring_ms"] = round((time.perf_counter() - scoring_start) * 1000)

    if provider_available:
        embedding_start = time.perf_counter()
        try:
            career_gaps, cached_count = _add_semantic_scores(provider, student_skill_names, skill_evidence, career_gaps)
            timings["cached_embeddings_used"] = cached_count
        except Exception:
            fallback_used = True
        timings["embedding_ms"] = round((time.perf_counter() - embedding_start) * 1000)

    # Build experience summary
    experience_summary = _summarize_experience(resume_data, linkedin_data)

    advisor_start = time.perf_counter()
    local_advisor = None
    if provider_available:
        try:
            local_advisor = provider.advise({
                "skills": student_skill_names[:40],
                "skill_evidence": skill_evidence[:20],
                "career_gaps": career_gaps[:5],
                "entrepreneurship_readiness": ent_score,
                "transcript_summary": _summarize_transcript(transcript_data) if transcript_data else None,
            })
        except Exception:
            fallback_used = True
    timings["advisor_ms"] = round((time.perf_counter() - advisor_start) * 1000)

    if session_id:
        _persist_skill_evidence(session_id, normalized, skill_evidence)

    return {
        "skills_inventory": _categorize_skills(student_skill_names),
        "total_skills_identified": len(student_skill_names),
        "normalized_skills": normalized,
        "skill_evidence": _merge_skill_evidence(normalized, skill_evidence),
        "entrepreneurship_readiness": ent_score,
        "career_gap_analysis": career_gaps,
        "experience_summary": experience_summary,
        "ai_insights": _legacy_insights_from_advisor(local_advisor),
        "local_advisor": local_advisor,
        "transcript_summary": _summarize_transcript(transcript_data) if transcript_data else None,
        "intelligence": provider.metadata(fallback_used=fallback_used),
        "performance": timings,
    }


def _extract_implicit_skills(text: str, skills_set: set):
    """Extract implicitly mentioned skills from achievement text."""
    keyword_map = {
        "revenue": "Revenue Forecasting",
        "financial model": "Financial Modeling",
        "data analy": "Statistical Analysis",
        "machine learn": "Machine Learning Fundamentals",
        "managed team": "Team Leadership",
        "led team": "Team Leadership",
        "project manage": "Project Management Tools",
        "market research": "Market Research Methods",
        "fundrais": "Fundraising Strategy",
        "pitch": "Pitching & Storytelling",
        "customer discover": "Customer Discovery",
        "product launch": "Go-to-Market Strategy",
        "growth": "Growth Marketing",
        "supply chain": "Supply Chain Management",
        "consulting": "Management Consulting Frameworks",
        "strategy": "Strategic Thinking",
        "negotiat": "Negotiation",
        "present": "Communication (Verbal)",
        "dashboard": "Data Visualization",
        "sql": "SQL & Database Management",
        "python": "Python Programming",
        "excel": "Excel / Google Sheets (Advanced)",
        "tableau": "Tableau / Power BI",
        "a/b test": "A/B Testing & Experimentation",
    }
    lower = text.lower()
    for keyword, skill in keyword_map.items():
        if keyword in lower:
            skills_set.add(skill)


def _categorize_skills(skill_names: list) -> dict:
    """Categorize skills by type."""
    skills_db = query("SELECT name, category, subcategory FROM skills")
    skill_lookup = {s["name"]: s for s in skills_db}

    categories = {
        "technical": [],
        "soft": [],
        "domain": [],
        "entrepreneurship": [],
        "uncategorized": [],
    }

    for name in skill_names:
        if name in skill_lookup:
            cat = skill_lookup[name]["category"]
            categories.get(cat, categories["uncategorized"]).append({
                "name": name,
                "subcategory": skill_lookup[name].get("subcategory", ""),
            })
        else:
            categories["uncategorized"].append({"name": name, "subcategory": ""})

    return categories


def _calculate_entrepreneurship_score(skill_names: list, transcript_data: dict = None) -> dict:
    """Calculate an entrepreneurship readiness score (0-100)."""
    ent_skills = query("SELECT name FROM skills WHERE category = 'entrepreneurship'")
    ent_skill_names = {s["name"] for s in ent_skills}

    student_ent = ent_skill_names & set(skill_names)
    skills_score = min(len(student_ent) / max(len(ent_skill_names), 1) * 60, 60)

    # Bonus for entrepreneurship courses
    course_bonus = 0
    if transcript_data:
        ent_courses = [c for c in transcript_data.get("courses", []) if "ENT" in c.get("course_code", "")]
        course_bonus = min(len(ent_courses) * 5, 20)

    # Bonus for startup experience
    exp_bonus = 0
    for skill in skill_names:
        if skill in ["Lean Startup Methodology", "Business Model Canvas", "Customer Discovery",
                      "Fundraising Strategy", "Pitching & Storytelling"]:
            exp_bonus = min(exp_bonus + 4, 20)

    total = min(skills_score + course_bonus + exp_bonus, 100)

    return {
        "score": round(total, 1),
        "out_of": 100,
        "entrepreneurship_skills_count": len(student_ent),
        "total_entrepreneurship_skills": len(ent_skill_names),
        "skills_present": sorted(student_ent),
        "skills_missing": sorted(ent_skill_names - student_ent)[:10],
        "interpretation": (
            "Strong entrepreneurial foundation" if total >= 70
            else "Developing entrepreneurial skills" if total >= 40
            else "Early-stage entrepreneurial readiness"
        ),
    }


def _analyze_career_gaps(student_skills: list) -> list:
    """Analyze skill gaps for common MBA career paths."""
    career_paths = [
        {"title": "Startup Founder", "industry": "Entrepreneurship"},
        {"title": "Management Consultant", "industry": "Consulting"},
        {"title": "Product Manager", "industry": "Technology"},
        {"title": "Investment Banking Associate", "industry": "Financial Services"},
        {"title": "Venture Capital Associate", "industry": "Financial Services"},
        {"title": "Marketing Manager", "industry": "Consumer Goods"},
        {"title": "Data Scientist", "industry": "Technology"},
    ]

    results = []
    student_set = set(student_skills)

    for path in career_paths:
        job_skills = query(
            """SELECT s.name, js.importance_score, js.frequency
            FROM job_skills js JOIN skills s ON js.skill_id = s.id
            WHERE js.job_title = ? AND js.industry = ?
            ORDER BY js.importance_score DESC""",
            (path["title"], path["industry"]),
        )

        if not job_skills:
            continue

        required = [s for s in job_skills if s["frequency"] == "essential"]
        common = [s for s in job_skills if s["frequency"] == "common"]

        matching = [s["name"] for s in job_skills if s["name"] in student_set]
        missing_essential = [s["name"] for s in required if s["name"] not in student_set]
        missing_common = [s["name"] for s in common if s["name"] not in student_set]

        match_pct = len(matching) / len(job_skills) * 100 if job_skills else 0

        results.append({
            "career_path": path["title"],
            "industry": path["industry"],
            "match_percentage": round(match_pct, 1),
            "matching_skills": matching,
            "missing_essential_skills": missing_essential,
            "missing_common_skills": missing_common,
            "total_required_skills": len(job_skills),
            "fit_level": (
                "Strong Fit" if match_pct >= 70
                else "Good Fit" if match_pct >= 50
                else "Developing" if match_pct >= 30
                else "Needs Development"
            ),
        })

    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return results


def _extract_missing_local_evidence(provider, source: str, parsed_data: dict | None) -> list:
    """Ask the local provider for evidence if parser did not already attach it."""
    if not parsed_data or parsed_data.get("skill_evidence"):
        return []
    raw_text = parsed_data.get("_raw_text", "")
    if not raw_text.strip():
        return []
    return provider.extract_profile_evidence(source, raw_text)


def _merge_skill_evidence(normalized: list, evidence: list) -> list:
    """Merge duplicate evidence while adding canonical skill names when available."""
    canonical_by_raw = {item["raw"]: item["canonical"] for item in normalized}
    merged = {}
    for item in evidence:
        raw_skill = item.get("skill", "").strip()
        if not raw_skill:
            continue
        canonical = canonical_by_raw.get(raw_skill, quick_normalize(raw_skill) or raw_skill)
        key = (canonical, item.get("source", ""), item.get("evidence_text", ""))
        current = merged.get(key)
        normalized_item = {
            "skill": canonical,
            "raw_skill": raw_skill,
            "evidence_text": item.get("evidence_text", ""),
            "source": item.get("source", "resume"),
            "confidence": round(float(item.get("confidence", 0.5)), 2),
            "evidence_type": item.get("evidence_type", "inferred"),
        }
        if not current or normalized_item["confidence"] > current["confidence"]:
            merged[key] = normalized_item
    return sorted(merged.values(), key=lambda x: x["confidence"], reverse=True)


def _persist_skill_evidence(session_id: str, normalized: list, evidence: list) -> None:
    execute("DELETE FROM skill_evidence WHERE session_id = ?", (session_id,))
    for item in _merge_skill_evidence(normalized, evidence):
        execute(
            """INSERT INTO skill_evidence
            (session_id, canonical_skill, raw_skill, source, evidence_text, confidence, match_method)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                item.get("skill"),
                item.get("raw_skill") or item.get("skill"),
                item.get("source", "resume"),
                item.get("evidence_text", ""),
                item.get("confidence", 0.5),
                item.get("evidence_type", "inferred"),
            ),
        )


def _add_semantic_scores(provider, student_skills: list, evidence: list, gaps: list) -> tuple[list, int]:
    """Add cached embedding-based scores without replacing deterministic overlap scoring."""
    profile_text = "; ".join(
        [item.get("evidence_text", "") for item in evidence if item.get("confidence", 0) >= 0.55][:20]
        or student_skills
    )
    if not profile_text.strip():
        return gaps, 0

    cached_count = 0
    profile_embedding = get_cached_embedding("profile", "current", provider, profile_text)
    if profile_embedding:
        cached_count += 1
    else:
        profile_embedding = provider.embed([profile_text])[0]
        cache_embedding("profile", "current", provider, profile_text, profile_embedding)

    updated = []
    for gap in gaps:
        career_text = " ".join([
            gap.get("career_path", ""),
            gap.get("industry", ""),
            " ".join(gap.get("matching_skills", [])),
            " ".join(gap.get("missing_essential_skills", [])),
            " ".join(gap.get("missing_common_skills", [])),
        ])
        entity_id = f"{gap.get('career_path')}::{gap.get('industry')}"
        career_embedding = get_cached_embedding("career_path", entity_id, provider, career_text)
        if career_embedding:
            cached_count += 1
        else:
            career_embedding = provider.embed([career_text])[0]
            cache_embedding("career_path", entity_id, provider, career_text, career_embedding)

        semantic = _cosine_similarity(profile_embedding, career_embedding)
        combined = (gap.get("match_percentage", 0) * 0.6) + (semantic * 100 * 0.25) + (_average_confidence(evidence) * 100 * 0.15)
        new_gap = {
            **gap,
            "semantic_match_score": round(semantic * 100, 1),
            "combined_match_score": round(combined, 1),
            "priority_missing_skills": gap.get("missing_essential_skills", [])[:5],
        }
        updated.append(new_gap)

    updated.sort(key=lambda x: x.get("combined_match_score", x.get("match_percentage", 0)), reverse=True)
    return updated, cached_count


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if not norm_a or not norm_b:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


def _average_confidence(evidence: list) -> float:
    values = [float(item.get("confidence", 0.5)) for item in evidence if item.get("confidence", 0) >= 0.55]
    return sum(values) / len(values) if values else 0.5


def _legacy_insights_from_advisor(advisor: dict | None) -> dict | None:
    if not advisor:
        return None
    return {
        "strengths": advisor.get("strengths", []),
        "development_areas": advisor.get("development_areas", []),
        "career_recommendations": [advisor.get("summary", "")] if advisor.get("summary") else [],
        "immediate_actions": advisor.get("recommended_next_steps", []),
        "entrepreneurship_assessment": advisor.get("summary", ""),
    }


def _summarize_experience(resume_data: dict = None, linkedin_data: dict = None) -> dict:
    """Summarize professional experience from resume and LinkedIn."""
    experiences = []
    if resume_data:
        experiences.extend(resume_data.get("experience", []))
    if linkedin_data:
        experiences.extend(linkedin_data.get("experience", []))

    industries = set()
    total_years = 0
    roles = []

    for exp in experiences:
        title = exp.get("title", "")
        company = exp.get("company", "")
        roles.append(f"{title} at {company}" if company else title)
        duration = exp.get("duration", "")
        if "year" in duration.lower():
            try:
                years = int(re.search(r'(\d+)', duration).group(1))
                total_years += years
            except (AttributeError, ValueError):
                pass

    return {
        "total_roles": len(experiences),
        "estimated_years_experience": total_years,
        "roles": roles[:5],
        "unique_companies": len({e.get("company") for e in experiences if e.get("company")}),
    }


def _summarize_transcript(transcript_data: dict) -> dict:
    """Summarize academic performance."""
    courses = transcript_data.get("courses", [])
    return {
        "institution": transcript_data.get("institution", ""),
        "program": transcript_data.get("program", ""),
        "gpa": transcript_data.get("cumulative_gpa"),
        "credits_completed": transcript_data.get("credits_completed", 0),
        "credits_required": transcript_data.get("credits_required", 0),
        "total_courses": len(courses),
        "core_courses": len([c for c in courses if c.get("course_type") == "Core"]),
        "elective_courses": len([c for c in courses if c.get("course_type") == "Elective"]),
        "top_courses": [
            c.get("name") or c.get("course_name", "") for c in sorted(
                [c for c in courses if c.get("grade", "").startswith("A")],
                key=lambda x: x.get("grade", ""),
            )[:5]
        ],
    }

