"""
LinkedIn PDF parser — extracts structured data from LinkedIn profile PDF exports.

LinkedIn allows users to export their profile as a PDF. This module
parses that PDF format to extract experience, skills, education, etc.
"""

import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ai.intelligence import get_intelligence_provider


def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def parse_with_ai(text: str) -> dict:
    """Use the configured local provider to enrich rule-based LinkedIn parsing."""
    parsed = parse_rule_based(text)
    try:
        provider = get_intelligence_provider()
        if provider.health().status == "ok":
            evidence = provider.extract_profile_evidence("linkedin", text)
            parsed["skill_evidence"] = evidence
            local_skills = [item["skill"] for item in evidence if item.get("skill") and item.get("confidence", 0) >= 0.55]
            parsed["skills"] = sorted(set(parsed.get("skills", []) + local_skills))
    except Exception:
        pass
    return parsed


def parse_rule_based(text: str) -> dict:
    """Rule-based LinkedIn PDF parser."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    result = {
        "name": "",
        "headline": "",
        "location": "",
        "about": "",
        "experience": [],
        "education": [],
        "skills": [],
        "certifications": [],
        "languages": [],
        "volunteer": [],
        "recommendations_count": 0,
        "connections_estimate": "Unknown",
    }

    # LinkedIn PDFs typically have: Name, Headline, Location at the top
    if len(lines) >= 1:
        result["name"] = lines[0]
    if len(lines) >= 2:
        result["headline"] = lines[1]
    if len(lines) >= 3 and not lines[2].lower().startswith(('experience', 'education', 'about')):
        result["location"] = lines[2]

    # Section detection
    current_section = None
    section_keywords = {
        "experience": ["experience"],
        "education": ["education"],
        "skills": ["skills", "top skills", "skills & endorsements"],
        "about": ["about", "summary"],
        "certifications": ["licenses & certifications", "certifications"],
        "languages": ["languages"],
        "volunteer": ["volunteer experience", "volunteer"],
    }

    section_content = {k: [] for k in section_keywords}
    for line in lines[3:]:
        lower = line.lower().strip()
        found_section = None
        for section, keywords in section_keywords.items():
            if lower in keywords or any(lower == kw for kw in keywords):
                found_section = section
                break
        if found_section:
            current_section = found_section
            continue
        if current_section:
            section_content[current_section].append(line)

    # Parse about
    result["about"] = " ".join(section_content["about"][:5])

    # Parse skills
    for line in section_content["skills"]:
        skills = re.split(r'[,;·•]', line)
        result["skills"].extend([s.strip() for s in skills if s.strip() and len(s.strip()) > 1])

    # Parse experience
    exp_lines = section_content["experience"]
    current_exp = None
    for line in exp_lines:
        # Heuristic: if line is short and doesn't start with bullet, it's likely a title/company
        if not line.startswith(('•', '-', '·')) and len(line) < 80:
            if current_exp:
                result["experience"].append(current_exp)
            current_exp = {
                "company": "",
                "title": line,
                "duration": "",
                "location": "",
                "description": "",
            }
        elif current_exp:
            if re.search(r'\d{4}', line) and ('present' in line.lower() or '-' in line):
                current_exp["duration"] = line
            elif current_exp["description"]:
                current_exp["description"] += " " + line
            else:
                current_exp["description"] = line
    if current_exp:
        result["experience"].append(current_exp)

    # Parse education
    edu_lines = section_content["education"]
    current_edu = None
    for line in edu_lines:
        edu_keywords = ['university', 'college', 'school', 'institute', 'academy']
        if any(kw in line.lower() for kw in edu_keywords):
            if current_edu:
                result["education"].append(current_edu)
            current_edu = {
                "institution": line,
                "degree": "",
                "field": "",
                "dates": "",
            }
        elif current_edu:
            if re.search(r'(mba|bachelor|master|b\.?s\.?|m\.?s\.?|ph\.?d)', line.lower()):
                current_edu["degree"] = line
            elif re.search(r'\d{4}', line):
                current_edu["dates"] = line
            elif not current_edu["field"]:
                current_edu["field"] = line
    if current_edu:
        result["education"].append(current_edu)

    # Parse certifications
    result["certifications"] = [line for line in section_content["certifications"] if line]

    # Parse languages
    result["languages"] = [line for line in section_content["languages"] if line and len(line) < 50]

    return result


def parse_linkedin(pdf_path: str) -> dict:
    """Main entry point: parse a LinkedIn PDF and return structured data."""
    text = extract_text_from_pdf(pdf_path)
    parsed = parse_with_ai(text)
    parsed["_raw_text"] = text[:5000]
    parsed["_source"] = "linkedin"
    return parsed
