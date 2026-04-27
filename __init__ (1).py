"""
Scraper for O*NET Web Services — pulls occupation data, skills, and knowledge areas.

O*NET provides free access to occupation data via their API.
Docs: https://services.onetcenter.org/reference/

This module fetches MBA-relevant occupations and their associated skills,
then maps them to our internal skills taxonomy.
"""

import json
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import ONET_BASE_URL

MBA_RELEVANT_OCCUPATIONS = [
    "11-1021.00",  # General and Operations Managers
    "11-2021.00",  # Marketing Managers
    "11-3031.00",  # Financial Managers
    "11-9199.00",  # Managers, All Other
    "13-1111.00",  # Management Analysts (Consultants)
    "13-2051.00",  # Financial and Insurance Analysts
    "13-2052.00",  # Personal Financial Advisors
    "13-2054.00",  # Financial Risk Specialists
    "13-2061.00",  # Financial Examiners
    "15-2051.00",  # Data Scientists
    "11-2022.00",  # Sales Managers
    "11-3021.00",  # Computer and Information Systems Managers
    "11-9041.00",  # Architectural and Engineering Managers
    "13-1082.00",  # Project Management Specialists
    "11-1011.00",  # Chief Executives
    "11-3111.00",  # Compensation and Benefits Managers
    "11-2032.00",  # Public Relations Managers
    "11-9198.00",  # Personal Service Managers
    "13-1161.00",  # Market Research Analysts
    "11-9121.00",  # Natural Sciences Managers
]

ONET_TO_INTERNAL_SKILL_MAP = {
    "Active Listening": "Active Listening",
    "Critical Thinking": "Critical Thinking",
    "Complex Problem Solving": "Problem Solving",
    "Judgment and Decision Making": "Decision Making Under Uncertainty",
    "Management of Financial Resources": "Financial Modeling",
    "Management of Personnel Resources": "Human Capital Management",
    "Negotiation": "Negotiation",
    "Persuasion": "Persuasion & Influence",
    "Social Perceptiveness": "Emotional Intelligence",
    "Speaking": "Communication (Verbal)",
    "Writing": "Communication (Written)",
    "Time Management": "Time Management",
    "Coordination": "Cross-functional Collaboration",
    "Monitoring": "Operations Strategy",
    "Systems Analysis": "Systems Thinking",
    "Systems Evaluation": "Analytical Reasoning",
    "Reading Comprehension": "Critical Thinking",
    "Active Learning": "Growth Mindset",
    "Mathematics": "Statistical Analysis",
    "Programming": "Python Programming",
    "Operations Analysis": "Operations Research",
    "Quality Control Analysis": "Quality Management (Six Sigma)",
    "Service Orientation": "Client Relationship Management",
    "Instructing": "Mentoring & Coaching",
}


def fetch_occupation_skills(occupation_code: str, auth: tuple = None) -> dict:
    """Fetch skills for a given O*NET occupation code."""
    headers = {"Accept": "application/json"}
    result = {"occupation_code": occupation_code, "skills": [], "knowledge": [], "abilities": []}

    for endpoint in ["skills", "knowledge", "abilities"]:
        url = f"{ONET_BASE_URL}/online/occupations/{occupation_code}/{endpoint}"
        try:
            resp = httpx.get(url, headers=headers, auth=auth, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                elements = data.get("element", [])
                for elem in elements:
                    entry = {
                        "id": elem.get("id", ""),
                        "name": elem.get("name", ""),
                        "description": elem.get("description", ""),
                        "score": elem.get("score", {}).get("value", 0),
                        "importance": elem.get("score", {}).get("value", 0),
                        "internal_skill": ONET_TO_INTERNAL_SKILL_MAP.get(elem.get("name")),
                    }
                    result[endpoint].append(entry)
        except httpx.RequestError:
            pass
        time.sleep(0.5)

    return result


def fetch_occupation_details(occupation_code: str, auth: tuple = None) -> dict:
    """Fetch basic details for an occupation."""
    url = f"{ONET_BASE_URL}/online/occupations/{occupation_code}"
    headers = {"Accept": "application/json"}
    try:
        resp = httpx.get(url, headers=headers, auth=auth, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "code": data.get("code", occupation_code),
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "sample_of_reported_titles": data.get("sample_of_reported_job_titles", {}).get("title", []),
            }
    except httpx.RequestError:
        pass
    return {"code": occupation_code, "title": "", "description": ""}


def scrape_all(auth: tuple = None, output_path: str = None) -> list:
    """Scrape all MBA-relevant occupations from O*NET."""
    results = []
    for code in MBA_RELEVANT_OCCUPATIONS:
        print(f"  Fetching O*NET data for {code}...")
        details = fetch_occupation_details(code, auth)
        skills = fetch_occupation_skills(code, auth)
        results.append({**details, **skills})
        time.sleep(1)

    if output_path:
        Path(output_path).write_text(json.dumps(results, indent=2))
        print(f"  Saved O*NET data to {output_path}")

    return results


if __name__ == "__main__":
    output = str(Path(__file__).parent.parent / "data" / "onet_occupations.json")
    Path(output).parent.mkdir(exist_ok=True)
    data = scrape_all(output_path=output)
    print(f"Scraped {len(data)} occupations from O*NET")
