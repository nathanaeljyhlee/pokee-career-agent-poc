"""
AI-powered profile analyzer — combines resume, LinkedIn, and transcript data
to produce a comprehensive student profile analysis.

Uses Claude for intelligent analysis when API key is available,
falls back to rule-based analysis otherwise.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from database.connection import query
from scrapers.skills_normalizer import normalize_skill_list, quick_normalize


def analyze_profile(resume_data: dict = None, linkedin_data: dict = None, transcript_data: dict = None) -> dict:
    """
    Analyze a student's combined profile and return:
    - Skills inventory (categorized)
    - Skill gaps vs. common MBA career paths
    - Entrepreneurship readiness score
    - Strengths and development areas
    - Career path suggestions
    """
    # Collect all raw skills from all sources
    raw_skills = set()

    if resume_data:
        raw_skills.update(resume_data.get("skills", []))
        for exp in resume_data.get("experience", []):
            for achievement in exp.get("key_achievements", []):
                _extract_implicit_skills(achievement, raw_skills)

    if linkedin_data:
        raw_skills.update(linkedin_data.get("skills", []))

    if transcript_data:
        for course in transcript_data.get("courses", []):
            raw_skills.update(course.get("skills_covered", []))

    # Normalize skills
    normalized = []
    skill_ids = set()
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

    # Get skill gaps for common paths
    career_gaps = _analyze_career_gaps(student_skill_names)

    # Build experience summary
    experience_summary = _summarize_experience(resume_data, linkedin_data)

    # AI-enhanced analysis if available
    ai_insights = None
    if ANTHROPIC_API_KEY:
        ai_insights = _get_ai_insights(resume_data, linkedin_data, transcript_data, student_skill_names)

    return {
        "skills_inventory": _categorize_skills(student_skill_names),
        "total_skills_identified": len(student_skill_names),
        "normalized_skills": normalized,
        "entrepreneurship_readiness": ent_score,
        "career_gap_analysis": career_gaps,
        "experience_summary": experience_summary,
        "ai_insights": ai_insights,
        "transcript_summary": _summarize_transcript(transcript_data) if transcript_data else None,
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


def _get_ai_insights(resume_data: dict, linkedin_data: dict, transcript_data: dict, skills: list) -> dict:
    """Get Claude-powered insights on the student's profile."""
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    profile_summary = json.dumps({
        "skills": skills[:30],
        "experience_count": len(resume_data.get("experience", [])) if resume_data else 0,
        "education": resume_data.get("education", []) if resume_data else [],
        "gpa": transcript_data.get("cumulative_gpa") if transcript_data else None,
        "program": transcript_data.get("program") if transcript_data else "MBA",
        "headline": linkedin_data.get("headline", "") if linkedin_data else "",
    }, indent=2)

    prompt = f"""You are a career advisor at Babson College. Analyze this MBA student's profile and provide actionable insights.

Student profile:
{profile_summary}

Return ONLY valid JSON:
{{
  "strengths": ["Top 3 strengths based on their profile"],
  "development_areas": ["Top 3 areas for growth"],
  "career_recommendations": ["Top 3 career path suggestions with brief rationale"],
  "immediate_actions": ["Top 3 specific, actionable next steps"],
  "entrepreneurship_assessment": "1-2 sentence assessment of their readiness to launch a venture"
}}"""

    try:
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.content[0].text
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass

    return {
        "strengths": ["Profile analysis requires AI processing"],
        "development_areas": ["Upload more documents for detailed analysis"],
        "career_recommendations": ["Complete your profile for personalized recommendations"],
        "immediate_actions": ["Add your resume and LinkedIn profile"],
        "entrepreneurship_assessment": "Complete profile for assessment",
    }
