"""
Academic transcript parser — handles both mock Workday data
and uploaded transcript PDFs.
"""

import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

GRADE_POINTS = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0,
    "P": None,  # Pass
    "W": None,  # Withdrawn
    "I": None,  # Incomplete
}


def parse_transcript_pdf(pdf_path: str) -> dict:
    """Parse an uploaded transcript PDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return parse_transcript_text(text)


def parse_transcript_text(text: str) -> dict:
    """Parse transcript text into structured data."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    result = {
        "student_name": "",
        "student_id": "",
        "program": "",
        "institution": "",
        "courses": [],
        "cumulative_gpa": None,
        "credits_completed": 0,
        "credits_required": 0,
        "semesters": [],
        "academic_standing": "Good Standing",
    }

    # Extract student name (usually near top)
    for line in lines[:10]:
        if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line):
            result["student_name"] = line
            break

    # Extract student ID
    for line in lines[:15]:
        id_match = re.search(r'(?:ID|Student\s*#?|SID)[:\s]*(\w+)', line, re.IGNORECASE)
        if id_match:
            result["student_id"] = id_match.group(1)
            break

    # Extract GPA
    for line in lines:
        gpa_match = re.search(r'(?:cumulative|overall|cum\.?)\s*GPA[:\s]*(\d\.\d+)', line, re.IGNORECASE)
        if gpa_match:
            result["cumulative_gpa"] = float(gpa_match.group(1))
            break

    # Extract courses
    course_pattern = re.compile(
        r'([A-Z]{2,4}\s*\d{3,4}[A-Z]?)\s+'  # Course code
        r'(.+?)\s+'                             # Course name
        r'(\d\.?\d?)\s+'                        # Credits
        r'([A-F][+-]?|P|W|I)',                  # Grade
        re.IGNORECASE
    )

    for line in lines:
        match = course_pattern.search(line)
        if match:
            code, name, credits, grade = match.groups()
            grade_point = GRADE_POINTS.get(grade.upper())
            result["courses"].append({
                "code": code.strip(),
                "name": name.strip(),
                "credits": float(credits),
                "grade": grade.upper(),
                "grade_points": grade_point,
                "semester": "",
            })

    # Calculate credits
    result["credits_completed"] = sum(c["credits"] for c in result["courses"])

    return result


def parse_workday_transcript(workday_data: dict) -> dict:
    """Convert Workday transcript data to our standard format."""
    courses = []
    for course in workday_data.get("courses", []):
        grade = course.get("grade", "")
        courses.append({
            "code": course.get("course_code", ""),
            "name": course.get("course_name", ""),
            "credits": course.get("credits", 3.0),
            "grade": grade,
            "grade_points": GRADE_POINTS.get(grade),
            "semester": course.get("semester", ""),
            "course_type": course.get("course_type", ""),
            "skills_covered": course.get("skills_covered", []),
        })

    return {
        "student_name": workday_data.get("student_name", ""),
        "student_id": workday_data.get("student_id", ""),
        "program": workday_data.get("program", "MBA"),
        "institution": workday_data.get("institution", "Babson College"),
        "courses": courses,
        "cumulative_gpa": workday_data.get("cumulative_gpa"),
        "credits_completed": sum(c["credits"] for c in courses),
        "credits_required": workday_data.get("credits_required", 60),
        "semesters": workday_data.get("semesters", []),
        "academic_standing": workday_data.get("academic_standing", "Good Standing"),
    }
