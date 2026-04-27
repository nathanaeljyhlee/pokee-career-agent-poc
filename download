"""
Resume PDF parser — extracts structured data from uploaded resume PDFs.

Uses PyMuPDF for text extraction and Claude for intelligent structuring.
Falls back to rule-based extraction if Claude is unavailable.
"""

import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def parse_with_ai(text: str) -> dict:
    """Use Claude to extract structured resume data."""
    if not ANTHROPIC_API_KEY:
        return parse_rule_based(text)

    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Analyze this resume text and extract structured data. Return ONLY valid JSON with these fields:

{{
  "name": "Full name",
  "email": "Email address or null",
  "phone": "Phone number or null",
  "location": "City, State or null",
  "summary": "Professional summary/objective (1-2 sentences)",
  "education": [
    {{
      "institution": "School name",
      "degree": "Degree type (e.g., MBA, BS)",
      "field": "Field of study",
      "graduation_year": 2024,
      "gpa": 3.8
    }}
  ],
  "experience": [
    {{
      "company": "Company name",
      "title": "Job title",
      "start_date": "Start date",
      "end_date": "End date or Present",
      "description": "Brief description",
      "key_achievements": ["Achievement 1", "Achievement 2"]
    }}
  ],
  "skills": ["Skill 1", "Skill 2"],
  "certifications": ["Cert 1"],
  "languages": ["English", "Spanish"],
  "interests": ["Interest 1"]
}}

Resume text:
{text[:8000]}"""

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        content = response.content[0].text
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json.loads(json_match.group())
    except (json.JSONDecodeError, IndexError):
        pass

    return parse_rule_based(text)


def parse_rule_based(text: str) -> dict:
    """Rule-based resume parser as fallback."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    result = {
        "name": lines[0] if lines else "Unknown",
        "email": None,
        "phone": None,
        "location": None,
        "summary": "",
        "education": [],
        "experience": [],
        "skills": [],
        "certifications": [],
        "languages": [],
        "interests": [],
    }

    # Extract email
    email_pattern = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
    for line in lines:
        match = email_pattern.search(line)
        if match:
            result["email"] = match.group()
            break

    # Extract phone
    phone_pattern = re.compile(r'[\(]?\d{3}[\)]?[-.\s]?\d{3}[-.\s]?\d{4}')
    for line in lines:
        match = phone_pattern.search(line)
        if match:
            result["phone"] = match.group()
            break

    # Extract skills section
    in_skills = False
    for line in lines:
        lower = line.lower()
        if any(keyword in lower for keyword in ['skills', 'technical skills', 'core competencies']):
            in_skills = True
            continue
        if in_skills:
            if any(keyword in lower for keyword in ['experience', 'education', 'work history', 'employment']):
                in_skills = False
                continue
            skills = re.split(r'[,;|•·]', line)
            result["skills"].extend([s.strip() for s in skills if s.strip() and len(s.strip()) > 1])

    # Extract education
    education_keywords = ['university', 'college', 'school of', 'institute', 'mba', 'bachelor', 'master', 'phd', 'b.s.', 'm.s.', 'b.a.', 'm.a.']
    for i, line in enumerate(lines):
        lower = line.lower()
        if any(kw in lower for kw in education_keywords):
            edu = {"institution": line, "degree": "", "field": "", "graduation_year": None, "gpa": None}
            year_match = re.search(r'20\d{2}', line)
            if year_match:
                edu["graduation_year"] = int(year_match.group())
            gpa_match = re.search(r'GPA[:\s]*(\d\.\d+)', line, re.IGNORECASE)
            if gpa_match:
                edu["gpa"] = float(gpa_match.group(1))
            degree_patterns = ['MBA', 'M.B.A.', 'BS', 'B.S.', 'BA', 'B.A.', 'MS', 'M.S.', 'MA', 'M.A.', 'PhD', 'Ph.D.']
            for dp in degree_patterns:
                if dp.lower() in lower:
                    edu["degree"] = dp
                    break
            result["education"].append(edu)

    # Extract experience (basic)
    experience_section = False
    current_exp = None
    for line in lines:
        lower = line.lower()
        if any(kw in lower for kw in ['experience', 'work history', 'employment', 'professional background']):
            experience_section = True
            continue
        if experience_section and any(kw in lower for kw in ['education', 'skills', 'certifications', 'interests']):
            if current_exp:
                result["experience"].append(current_exp)
            experience_section = False
            continue
        if experience_section:
            year_match = re.search(r'20\d{2}', line)
            if year_match and len(line) < 100:
                if current_exp:
                    result["experience"].append(current_exp)
                current_exp = {
                    "company": "",
                    "title": line,
                    "start_date": "",
                    "end_date": "",
                    "description": "",
                    "key_achievements": [],
                }
            elif current_exp and line.startswith(('•', '-', '·', '*')):
                current_exp["key_achievements"].append(line.lstrip('•-·* '))

    if current_exp:
        result["experience"].append(current_exp)

    return result


def parse_resume(pdf_path: str) -> dict:
    """Main entry point: parse a resume PDF and return structured data."""
    text = extract_text_from_pdf(pdf_path)
    parsed = parse_with_ai(text)
    parsed["_raw_text"] = text[:5000]
    parsed["_source"] = "resume"
    return parsed
