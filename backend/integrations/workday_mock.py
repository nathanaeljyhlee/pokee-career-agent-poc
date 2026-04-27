"""
Mock Workday Student adapter.

Simulates Workday Student API responses for development/testing.
Designed with a clean interface so the real Workday SOAP/REST API
can be swapped in later.

Toggle via WORKDAY_MODE env var: "mock" or "live"
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import WORKDAY_MODE

# Babson MBA curriculum structure
BABSON_CORE_COURSES = [
    {"code": "ACT6100", "name": "Financial Reporting and Analysis", "credits": 3.0, "semester": "Fall 1", "skills": ["Accounting (GAAP)", "Financial Modeling"]},
    {"code": "ENT6200", "name": "Entrepreneurial Thought and Action", "credits": 3.0, "semester": "Fall 1", "skills": ["Business Model Canvas", "Lean Startup Methodology", "Customer Discovery"]},
    {"code": "FIN7200", "name": "Corporate Financial Management", "credits": 3.0, "semester": "Fall 1", "skills": ["Financial Modeling", "Valuation Methods"]},
    {"code": "MOB7200", "name": "Leading and Managing People", "credits": 3.0, "semester": "Fall 1", "skills": ["Team Leadership", "Change Management", "Emotional Intelligence"]},
    {"code": "MKT7400", "name": "Marketing Management", "credits": 3.0, "semester": "Spring 1", "skills": ["Marketing Strategy", "Market Research Methods"]},
    {"code": "OPM7100", "name": "Operations Management", "credits": 3.0, "semester": "Spring 1", "skills": ["Supply Chain Analytics", "Operations Strategy"]},
    {"code": "QTM6100", "name": "Data Analytics for Managers", "credits": 3.0, "semester": "Spring 1", "skills": ["Statistical Analysis", "Data Visualization", "Python Programming"]},
    {"code": "STR7200", "name": "Strategy Formulation", "credits": 3.0, "semester": "Spring 1", "skills": ["Corporate Strategy", "Strategic Thinking", "Competitive Analysis"]},
    {"code": "ECN6100", "name": "Managerial Economics", "credits": 3.0, "semester": "Fall 1", "skills": ["Econometrics", "Decision Making Under Uncertainty"]},
    {"code": "LAW7100", "name": "Legal Environment of Business", "credits": 1.5, "semester": "Spring 1", "skills": ["Regulatory Compliance", "Contract Negotiation"]},
]

BABSON_ELECTIVES = [
    {"code": "ENT7500", "name": "Venture Growth Strategies", "credits": 3.0, "skills": ["Scaling Operations", "Growth Hacking", "Unit Economics"]},
    {"code": "FIN7500", "name": "Venture Finance", "credits": 3.0, "skills": ["Venture Financing", "Cap Table Management", "Fundraising Strategy"]},
    {"code": "ENT7200", "name": "New Venture Creation", "credits": 3.0, "skills": ["Business Model Canvas", "Customer Discovery", "Market Sizing (TAM/SAM/SOM)"]},
    {"code": "STR8300", "name": "Competitive Strategy", "credits": 3.0, "skills": ["Corporate Strategy", "Competitive Analysis"]},
    {"code": "MKT8400", "name": "Digital Marketing Strategy", "credits": 3.0, "skills": ["SEO / SEM", "Social Media Analytics", "Digital Marketing Analytics"]},
    {"code": "FIN8500", "name": "Private Equity & Venture Capital", "credits": 3.0, "skills": ["Private Equity", "Venture Capital", "Valuation Methods"]},
    {"code": "TEC8100", "name": "AI for Business Leaders", "credits": 3.0, "skills": ["AI Strategy & Governance", "Machine Learning Fundamentals"]},
    {"code": "ENT8600", "name": "Social Innovation & Impact", "credits": 3.0, "skills": ["Social Enterprise Models", "Impact Measurement"]},
    {"code": "FIN8200", "name": "Investment Management", "credits": 3.0, "skills": ["Quantitative Risk Analysis", "Financial Modeling"]},
    {"code": "MKT8600", "name": "Consumer Behavior", "credits": 3.0, "skills": ["Market Research Methods", "Pricing Strategy Models"]},
    {"code": "ENT8400", "name": "Family Business Management", "credits": 3.0, "skills": ["Family Business Management", "Corporate Strategy"]},
    {"code": "TEC8200", "name": "Product Management", "credits": 3.0, "skills": ["Technology Product Management", "Agile / Scrum Methodology", "UX/UI Design Principles"]},
    {"code": "ENT8800", "name": "Startup Consulting Practicum", "credits": 3.0, "skills": ["Management Consulting Frameworks", "Customer Discovery", "Business Development"]},
    {"code": "FIN8400", "name": "FinTech Innovation", "credits": 3.0, "skills": ["FinTech", "Blockchain Fundamentals", "Regulatory Compliance"]},
    {"code": "OPM8200", "name": "Supply Chain Strategy", "credits": 3.0, "skills": ["Supply Chain Management", "Operations Research", "Supply Chain Analytics"]},
]

MOCK_STUDENTS = [
    {
        "student_id": "B00123456",
        "student_name": "Alex Chen",
        "email": "achen@babson.edu",
        "program": "Full-Time MBA",
        "concentration": "Entrepreneurship",
        "enrollment_status": "Active",
        "start_term": "Fall 2023",
        "expected_graduation": "Spring 2025",
        "credits_required": 60,
        "academic_standing": "Good Standing",
        "cumulative_gpa": 3.72,
        "completed_semesters": ["Fall 2023", "Spring 2024", "Fall 2024"],
        "elective_indices": [0, 1, 2, 6, 11],
    },
    {
        "student_id": "B00234567",
        "student_name": "Sarah Johnson",
        "email": "sjohnson@babson.edu",
        "program": "Full-Time MBA",
        "concentration": "Finance",
        "enrollment_status": "Active",
        "start_term": "Fall 2023",
        "expected_graduation": "Spring 2025",
        "credits_required": 60,
        "academic_standing": "Good Standing",
        "cumulative_gpa": 3.85,
        "completed_semesters": ["Fall 2023", "Spring 2024", "Fall 2024"],
        "elective_indices": [3, 5, 8, 13, 9],
    },
    {
        "student_id": "B00345678",
        "student_name": "Marcus Williams",
        "email": "mwilliams@babson.edu",
        "program": "Full-Time MBA",
        "concentration": None,
        "enrollment_status": "Active",
        "start_term": "Fall 2024",
        "expected_graduation": "Spring 2026",
        "credits_required": 60,
        "academic_standing": "Good Standing",
        "cumulative_gpa": 3.55,
        "completed_semesters": ["Fall 2024"],
        "elective_indices": [],
    },
]


def _generate_grade(gpa_target: float) -> str:
    """Generate a realistic grade given a target GPA."""
    r = random.random()
    if gpa_target >= 3.7:
        if r < 0.4:
            return "A"
        elif r < 0.75:
            return "A-"
        elif r < 0.95:
            return "B+"
        return "B"
    elif gpa_target >= 3.3:
        if r < 0.2:
            return "A"
        elif r < 0.5:
            return "A-"
        elif r < 0.8:
            return "B+"
        return "B"
    else:
        if r < 0.1:
            return "A-"
        elif r < 0.35:
            return "B+"
        elif r < 0.7:
            return "B"
        elif r < 0.9:
            return "B-"
        return "C+"


def _build_transcript(student: dict) -> dict:
    """Build a complete transcript for a mock student."""
    random.seed(hash(student["student_id"]))
    courses = []

    # Add core courses with grades
    for course in BABSON_CORE_COURSES:
        sem = course["semester"]
        if sem.replace("1", "2023" if "Fall" in sem else "2024") in " ".join(student["completed_semesters"]) or True:
            courses.append({
                "course_code": course["code"],
                "course_name": course["name"],
                "credits": course["credits"],
                "grade": _generate_grade(student["cumulative_gpa"]),
                "semester": course["semester"],
                "course_type": "Core",
                "skills_covered": course["skills"],
            })

    # Add electives
    for idx in student["elective_indices"]:
        elective = BABSON_ELECTIVES[idx]
        sem_num = student["elective_indices"].index(idx)
        semesters = ["Fall 2", "Spring 2", "Fall 2", "Spring 2"]
        semester = semesters[sem_num] if sem_num < len(semesters) else "Spring 2"
        courses.append({
            "course_code": elective["code"],
            "course_name": elective["name"],
            "credits": elective["credits"],
            "grade": _generate_grade(student["cumulative_gpa"]),
            "semester": semester,
            "course_type": "Elective",
            "skills_covered": elective["skills"],
        })

    return {
        "student_id": student["student_id"],
        "student_name": student["student_name"],
        "email": student["email"],
        "program": student["program"],
        "concentration": student["concentration"],
        "institution": "Babson College - F.W. Olin Graduate School of Business",
        "enrollment_status": student["enrollment_status"],
        "start_term": student["start_term"],
        "expected_graduation": student["expected_graduation"],
        "academic_standing": student["academic_standing"],
        "cumulative_gpa": student["cumulative_gpa"],
        "credits_completed": sum(c["credits"] for c in courses),
        "credits_required": student["credits_required"],
        "courses": courses,
        "semesters": student["completed_semesters"],
    }


class WorkdayAdapter:
    """Interface for Workday Student API (mock or live)."""

    def __init__(self, mode: str = None):
        self.mode = mode or WORKDAY_MODE

    def get_transcript(self, student_id: str = None) -> dict:
        if self.mode == "mock":
            return self._mock_transcript(student_id)
        return self._live_transcript(student_id)

    def get_student_info(self, student_id: str = None) -> dict:
        if self.mode == "mock":
            return self._mock_student_info(student_id)
        return self._live_student_info(student_id)

    def _mock_transcript(self, student_id: str = None) -> dict:
        if student_id:
            student = next((s for s in MOCK_STUDENTS if s["student_id"] == student_id), None)
            if student:
                return _build_transcript(student)
        return _build_transcript(MOCK_STUDENTS[0])

    def _mock_student_info(self, student_id: str = None) -> dict:
        if student_id:
            student = next((s for s in MOCK_STUDENTS if s["student_id"] == student_id), None)
            if student:
                return {k: v for k, v in student.items() if k != "elective_indices"}
        s = MOCK_STUDENTS[0]
        return {k: v for k, v in s.items() if k != "elective_indices"}

    def _live_transcript(self, student_id: str) -> dict:
        raise NotImplementedError(
            "Live Workday integration requires institutional API credentials. "
            "Set WORKDAY_MODE=mock for development."
        )

    def _live_student_info(self, student_id: str) -> dict:
        raise NotImplementedError(
            "Live Workday integration requires institutional API credentials. "
            "Set WORKDAY_MODE=mock for development."
        )

    def list_mock_students(self) -> list:
        return [
            {"student_id": s["student_id"], "name": s["student_name"], "program": s["program"]}
            for s in MOCK_STUDENTS
        ]
