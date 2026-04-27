"""
Recommendation engine — suggests courses, projects, and jobs
based on the student's profile analysis and skill gaps.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.connection import query


def recommend_courses(student_skills: list, skill_gaps: list, completed_courses: list = None, school: str = "Babson", limit: int = 10) -> list:
    """
    Recommend courses that address the student's skill gaps.
    Prioritizes courses that cover the most missing essential skills.
    """
    completed_codes = {c.get("course_code", c.get("code", "")) for c in (completed_courses or [])}

    missing_skills = set()
    for gap in skill_gaps:
        missing_skills.update(gap.get("missing_essential_skills", []))
        missing_skills.update(gap.get("missing_common_skills", []))

    courses = query(
        "SELECT c.*, s.short_name as school_name FROM courses c JOIN schools s ON c.school_id = s.id"
    )

    scored_courses = []
    for course in courses:
        if course.get("course_code") in completed_codes:
            continue

        skills_taught = json.loads(course.get("skills_taught", "[]")) if isinstance(course.get("skills_taught"), str) else course.get("skills_taught", [])

        addressed_gaps = set(skills_taught) & missing_skills
        new_skills = set(skills_taught) - set(student_skills)

        if not addressed_gaps and not new_skills:
            continue

        # Score: prioritize gap coverage, then new skill acquisition
        score = len(addressed_gaps) * 3 + len(new_skills) * 1

        # Bonus for Babson courses (home school)
        if course.get("school_name") == school:
            score *= 1.5

        scored_courses.append({
            "course_id": course["id"],
            "course_code": course.get("course_code", ""),
            "name": course["name"],
            "school": course.get("school_name", ""),
            "description": course.get("description", ""),
            "credits": course.get("credits", 3.0),
            "is_elective": bool(course.get("is_elective", True)),
            "semester": course.get("semester", ""),
            "skills_taught": skills_taught,
            "gaps_addressed": sorted(addressed_gaps),
            "new_skills": sorted(new_skills),
            "relevance_score": round(score, 1),
            "rationale": _build_course_rationale(addressed_gaps, new_skills, course["name"]),
        })

    scored_courses.sort(key=lambda x: x["relevance_score"], reverse=True)
    return scored_courses[:limit]


def recommend_projects(student_skills: list, skill_gaps: list, interests: list = None, limit: int = 8) -> list:
    """
    Recommend projects that build missing skills and align with interests.
    """
    missing_skills = set()
    for gap in skill_gaps:
        missing_skills.update(gap.get("missing_essential_skills", []))
        missing_skills.update(gap.get("missing_common_skills", []))

    projects = query("SELECT * FROM projects")
    interest_set = {i.lower() for i in (interests or [])}

    scored_projects = []
    for project in projects:
        skills_dev = json.loads(project.get("skills_developed", "[]")) if isinstance(project.get("skills_developed"), str) else project.get("skills_developed", [])
        industries = json.loads(project.get("industry_relevance", "[]")) if isinstance(project.get("industry_relevance"), str) else project.get("industry_relevance", [])

        gaps_addressed = set(skills_dev) & missing_skills
        new_skills = set(skills_dev) - set(student_skills)

        if not gaps_addressed and not new_skills:
            continue

        score = len(gaps_addressed) * 3 + len(new_skills) * 1

        # Industry interest bonus
        if interest_set:
            industry_match = len({i.lower() for i in industries} & interest_set)
            score += industry_match * 2

        scored_projects.append({
            "project_id": project["id"],
            "title": project["title"],
            "description": project["description"],
            "project_type": project.get("project_type", "independent"),
            "difficulty": project.get("difficulty", "intermediate"),
            "estimated_hours": project.get("estimated_hours", 80),
            "skills_developed": skills_dev,
            "industry_relevance": industries,
            "gaps_addressed": sorted(gaps_addressed),
            "new_skills": sorted(new_skills),
            "relevance_score": round(score, 1),
            "rationale": _build_project_rationale(gaps_addressed, project["title"], project.get("project_type", "")),
        })

    scored_projects.sort(key=lambda x: x["relevance_score"], reverse=True)
    return scored_projects[:limit]


def recommend_jobs(student_skills: list, career_gaps: list, preferences: dict = None, limit: int = 10) -> list:
    """
    Recommend jobs based on skill match and career gap analysis.
    """
    from scrapers.job_postings import get_all_postings

    prefs = preferences or {}
    preferred_industries = {i.lower() for i in prefs.get("industries", [])}
    min_salary = prefs.get("min_salary", 0)

    postings = get_all_postings()
    student_set = set(student_skills)

    scored_jobs = []
    for posting in postings:
        salary_min = posting.get("salary_range", {}).get("min", 0)
        if salary_min < min_salary:
            continue

        required = set(posting.get("required_skills", []))
        preferred = set(posting.get("preferred_skills", []))

        matching_required = required & student_set
        matching_preferred = preferred & student_set
        missing_required = required - student_set
        missing_preferred = preferred - student_set

        if not matching_required:
            continue

        req_match_pct = len(matching_required) / len(required) * 100 if required else 0
        total_match_pct = (len(matching_required) + len(matching_preferred)) / (len(required) + len(preferred)) * 100 if (required or preferred) else 0

        score = req_match_pct * 0.7 + total_match_pct * 0.3

        # Industry preference bonus
        if preferred_industries and posting.get("industry", "").lower() in preferred_industries:
            score *= 1.2

        # Career gap alignment
        for gap in career_gaps:
            if gap["career_path"].lower() in posting["title"].lower():
                score *= 1.1
                break

        scored_jobs.append({
            "title": posting["title"],
            "company_type": posting.get("company_type", ""),
            "industry": posting.get("industry", ""),
            "location": posting.get("location", ""),
            "salary_range": posting.get("salary_range", {}),
            "experience_required": posting.get("experience_required", ""),
            "description": posting.get("description", ""),
            "matching_skills": sorted(matching_required | matching_preferred),
            "missing_required_skills": sorted(missing_required),
            "missing_preferred_skills": sorted(missing_preferred),
            "required_match_pct": round(req_match_pct, 1),
            "total_match_pct": round(total_match_pct, 1),
            "relevance_score": round(score, 1),
            "rationale": _build_job_rationale(posting["title"], req_match_pct, missing_required),
        })

    scored_jobs.sort(key=lambda x: x["relevance_score"], reverse=True)
    return scored_jobs[:limit]


def _build_course_rationale(gaps_addressed: set, new_skills: set, course_name: str) -> str:
    parts = []
    if gaps_addressed:
        skills_str = ", ".join(list(gaps_addressed)[:3])
        parts.append(f"Fills skill gaps in {skills_str}")
    if new_skills:
        skills_str = ", ".join(list(new_skills)[:2])
        parts.append(f"builds new skills: {skills_str}")
    return ". ".join(parts) + "." if parts else f"{course_name} aligns with your career goals."


def _build_project_rationale(gaps_addressed: set, title: str, project_type: str) -> str:
    if gaps_addressed:
        skills_str = ", ".join(list(gaps_addressed)[:3])
        return f"This {project_type} project develops {skills_str} through hands-on experience."
    return f"{title} provides practical experience relevant to your career goals."


def _build_job_rationale(title: str, match_pct: float, missing: set) -> str:
    if match_pct >= 80:
        return f"Strong match for {title} — you have most required skills."
    elif match_pct >= 60:
        gap_str = ", ".join(list(missing)[:2])
        return f"Good match for {title}. Focus on developing: {gap_str}."
    else:
        gap_str = ", ".join(list(missing)[:3])
        return f"Developing match for {title}. Key gaps: {gap_str}."


def get_comparison_data(school_names: list = None) -> list:
    """Get comparison data across schools for the explore page."""
    if school_names:
        placeholders = ",".join(["?"] * len(school_names))
        schools = query(f"SELECT * FROM schools WHERE short_name IN ({placeholders})", tuple(school_names))
    else:
        schools = query("SELECT * FROM schools ORDER BY ranking_us_news")

    results = []
    for school in schools:
        outcomes = query(
            """SELECT industry, AVG(median_salary) as avg_salary, AVG(employment_rate_6mo) as avg_emp_rate,
               COUNT(*) as data_points
            FROM job_outcomes WHERE school_id = ?
            GROUP BY industry ORDER BY avg_salary DESC""",
            (school["id"],),
        )

        results.append({
            "school": school["short_name"],
            "full_name": school["name"],
            "type": school["school_type"],
            "ranking_us_news": school["ranking_us_news"],
            "ranking_entrepreneurship": school.get("ranking_entrepreneurship"),
            "outcomes_by_industry": [
                {
                    "industry": o["industry"],
                    "avg_salary": round(o["avg_salary"]) if o["avg_salary"] else None,
                    "employment_rate": round(o["avg_emp_rate"] * 100, 1) if o["avg_emp_rate"] else None,
                }
                for o in outcomes
            ],
        })

    return results
