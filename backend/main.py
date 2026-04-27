"""
Babson MBA Career Intelligence Platform — FastAPI Backend

Provides endpoints for:
- Resume/LinkedIn PDF upload and parsing
- Workday transcript integration (mock)
- AI-powered profile analysis
- Course, project, and job recommendations
- School comparison data
"""

import json
import os
import sys
import uuid
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import CORS_ORIGINS, UPLOAD_DIR
from database.connection import init_db, query, query_one, execute
from parsers.resume_parser import parse_resume
from parsers.linkedin_parser import parse_linkedin
from parsers.transcript_parser import parse_workday_transcript
from integrations.workday_mock import WorkdayAdapter
from ai.profile_analyzer import analyze_profile
from ai.recommender import recommend_courses, recommend_projects, recommend_jobs, get_comparison_data
from ai.intelligence import get_intelligence_provider

app = FastAPI(
    title="Babson MBA Career Intelligence Platform",
    version="1.0.0",
    description="AI-powered career guidance for MBA students",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workday = WorkdayAdapter()

# In-memory session store (would use Redis in production)
sessions: dict = {}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class AnalyzeRequest(BaseModel):
    session_id: str
    target_roles: list[str] = []
    preferred_industries: list[str] = []
    min_salary: int = 0


class CompareRequest(BaseModel):
    student_skills: list[str]
    target_role: str
    target_industry: str


class WorkdayConnectRequest(BaseModel):
    session_id: str
    student_id: str = None


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    init_db()


# ---------------------------------------------------------------------------
# Upload endpoints
# ---------------------------------------------------------------------------
@app.post("/api/upload/resume")
async def upload_resume(file: UploadFile = File(...), session_id: str = Query(None)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    sid = session_id or str(uuid.uuid4())
    filepath = UPLOAD_DIR / f"{sid}_resume.pdf"
    content = await file.read()
    filepath.write_bytes(content)

    parsed = parse_resume(str(filepath))
    sessions.setdefault(sid, {})["resume"] = parsed

    return {
        "session_id": sid,
        "status": "success",
        "filename": file.filename,
        "parsed": {
            "name": parsed.get("name"),
            "email": parsed.get("email"),
            "skills_count": len(parsed.get("skills", [])),
            "experience_count": len(parsed.get("experience", [])),
            "education_count": len(parsed.get("education", [])),
        },
    }


@app.post("/api/upload/linkedin")
async def upload_linkedin(file: UploadFile = File(...), session_id: str = Query(None)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    sid = session_id or str(uuid.uuid4())
    filepath = UPLOAD_DIR / f"{sid}_linkedin.pdf"
    content = await file.read()
    filepath.write_bytes(content)

    parsed = parse_linkedin(str(filepath))
    sessions.setdefault(sid, {})["linkedin"] = parsed

    return {
        "session_id": sid,
        "status": "success",
        "filename": file.filename,
        "parsed": {
            "name": parsed.get("name"),
            "headline": parsed.get("headline"),
            "skills_count": len(parsed.get("skills", [])),
            "experience_count": len(parsed.get("experience", [])),
        },
    }


# ---------------------------------------------------------------------------
# Workday (mock) endpoints
# ---------------------------------------------------------------------------
@app.post("/api/workday/connect")
async def workday_connect(request: WorkdayConnectRequest):
    transcript = workday.get_transcript(request.student_id)
    parsed = parse_workday_transcript(transcript)
    sessions.setdefault(request.session_id, {})["transcript"] = parsed

    return {
        "session_id": request.session_id,
        "status": "success",
        "mode": workday.mode,
        "student": {
            "name": transcript.get("student_name"),
            "program": transcript.get("program"),
            "gpa": transcript.get("cumulative_gpa"),
            "courses_count": len(transcript.get("courses", [])),
            "credits_completed": sum(c.get("credits", 0) for c in transcript.get("courses", [])),
        },
    }


@app.get("/api/workday/students")
async def list_mock_students():
    return {"students": workday.list_mock_students(), "mode": workday.mode}


# ---------------------------------------------------------------------------
# Analysis endpoints
# ---------------------------------------------------------------------------
@app.post("/api/analyze/profile")
async def analyze_student_profile(request: AnalyzeRequest):
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(404, "Session not found. Upload documents first.")

    resume_data = session.get("resume")
    linkedin_data = session.get("linkedin")
    transcript_data = session.get("transcript")

    if not resume_data and not linkedin_data and not transcript_data:
        raise HTTPException(400, "No documents uploaded. Please upload at least one document.")

    analysis = analyze_profile(resume_data, linkedin_data, transcript_data, session_id=request.session_id)
    session["analysis"] = analysis

    # Persist to DB
    all_skills = []
    for cat_skills in analysis.get("skills_inventory", {}).values():
        all_skills.extend([s["name"] for s in cat_skills])

    execute(
        """INSERT OR REPLACE INTO student_profiles
        (session_id, name, resume_data, linkedin_data, transcript_data, extracted_skills, analysis_result)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            request.session_id,
            (resume_data or {}).get("name") or (linkedin_data or {}).get("name") or "",
            json.dumps(resume_data) if resume_data else None,
            json.dumps(linkedin_data) if linkedin_data else None,
            json.dumps(transcript_data) if transcript_data else None,
            json.dumps(all_skills),
            json.dumps(analysis),
        ),
    )

    return {"session_id": request.session_id, "analysis": analysis}


# ---------------------------------------------------------------------------
# Recommendation endpoints
# ---------------------------------------------------------------------------
@app.get("/api/recommend/courses")
async def get_course_recommendations(session_id: str, limit: int = 10):
    session = sessions.get(session_id)
    if not session or "analysis" not in session:
        raise HTTPException(404, "Run analysis first via /api/analyze/profile")

    analysis = session["analysis"]
    all_skills = []
    for cat_skills in analysis.get("skills_inventory", {}).values():
        all_skills.extend([s["name"] for s in cat_skills])

    completed = []
    if session.get("transcript"):
        completed = session["transcript"].get("courses", [])

    courses = recommend_courses(
        student_skills=all_skills,
        skill_gaps=analysis.get("career_gap_analysis", []),
        completed_courses=completed,
        limit=limit,
    )

    return {"session_id": session_id, "recommendations": courses, "total": len(courses)}


@app.get("/api/recommend/projects")
async def get_project_recommendations(session_id: str, limit: int = 8):
    session = sessions.get(session_id)
    if not session or "analysis" not in session:
        raise HTTPException(404, "Run analysis first via /api/analyze/profile")

    analysis = session["analysis"]
    all_skills = []
    for cat_skills in analysis.get("skills_inventory", {}).values():
        all_skills.extend([s["name"] for s in cat_skills])

    projects = recommend_projects(
        student_skills=all_skills,
        skill_gaps=analysis.get("career_gap_analysis", []),
        limit=limit,
    )

    return {"session_id": session_id, "recommendations": projects, "total": len(projects)}


@app.get("/api/recommend/jobs")
async def get_job_recommendations(session_id: str, limit: int = 10):
    session = sessions.get(session_id)
    if not session or "analysis" not in session:
        raise HTTPException(404, "Run analysis first via /api/analyze/profile")

    analysis = session["analysis"]
    all_skills = []
    for cat_skills in analysis.get("skills_inventory", {}).values():
        all_skills.extend([s["name"] for s in cat_skills])

    jobs = recommend_jobs(
        student_skills=all_skills,
        career_gaps=analysis.get("career_gap_analysis", []),
        limit=limit,
    )

    return {"session_id": session_id, "recommendations": jobs, "total": len(jobs)}


# ---------------------------------------------------------------------------
# Data exploration endpoints
# ---------------------------------------------------------------------------
@app.get("/api/data/outcomes/{school}")
async def get_school_outcomes(school: str):
    school_row = query_one("SELECT * FROM schools WHERE short_name = ?", (school,))
    if not school_row:
        raise HTTPException(404, f"School '{school}' not found")

    outcomes = query(
        "SELECT * FROM job_outcomes WHERE school_id = ? ORDER BY industry",
        (school_row["id"],),
    )

    return {
        "school": dict(school_row),
        "outcomes": [dict(o) for o in outcomes],
        "total": len(outcomes),
    }


@app.get("/api/data/skills/taxonomy")
async def get_skills_taxonomy():
    skills = query("SELECT * FROM skills ORDER BY category, name")
    by_category: dict = {}
    for s in skills:
        cat = s["category"]
        by_category.setdefault(cat, []).append(dict(s))
    return {
        "taxonomy": by_category,
        "total": len(skills),
        "categories": list(by_category.keys()),
    }


@app.get("/api/data/skills/{industry}")
async def get_industry_skills(industry: str):
    skills = query(
        """SELECT s.name, s.category, js.importance_score, js.frequency, js.job_title
        FROM job_skills js JOIN skills s ON js.skill_id = s.id
        WHERE js.industry = ?
        ORDER BY js.importance_score DESC""",
        (industry,),
    )

    if not skills:
        raise HTTPException(404, f"No skills data found for industry '{industry}'")

    return {"industry": industry, "skills": [dict(s) for s in skills], "total": len(skills)}


@app.post("/api/data/compare")
async def compare_skills(request: CompareRequest):
    from scrapers.skills_normalizer import get_skill_gaps

    job_skills = query(
        """SELECT s.name FROM job_skills js JOIN skills s ON js.skill_id = s.id
        WHERE js.job_title = ? AND js.industry = ?""",
        (request.target_role, request.target_industry),
    )
    target_skills = [s["name"] for s in job_skills]

    if not target_skills:
        raise HTTPException(404, f"No skill data for {request.target_role} in {request.target_industry}")

    gaps = get_skill_gaps(request.student_skills, target_skills)
    return {"comparison": gaps}


@app.get("/api/data/schools")
async def list_schools():
    schools = query("SELECT * FROM schools ORDER BY ranking_us_news")
    return {"schools": [dict(s) for s in schools]}


@app.get("/api/data/schools/compare")
async def compare_schools(schools: str = Query(None, description="Comma-separated school short names")):
    school_names = [s.strip() for s in schools.split(",")] if schools else None
    comparison = get_comparison_data(school_names)
    return {"comparison": comparison}


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    return {
        "session_id": session_id,
        "has_resume": "resume" in session,
        "has_linkedin": "linkedin" in session,
        "has_transcript": "transcript" in session,
        "has_analysis": "analysis" in session,
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/intelligence/health")
async def intelligence_health():
    provider = get_intelligence_provider()
    return provider.metadata()
