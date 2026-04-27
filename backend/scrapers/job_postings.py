"""
Job postings data collector for MBA-relevant positions in the Boston area.

Since direct scraping of job boards may violate ToS, this module:
1. Uses curated data representing typical MBA-level job postings
2. Provides an interface to plug in Indeed/LinkedIn APIs when available
3. Maps job requirements to our internal skills taxonomy
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Representative MBA-level job postings for Boston area
MBA_JOB_POSTINGS = [
    {
        "title": "Associate Product Manager",
        "company_type": "Tech (Large)",
        "industry": "Technology",
        "location": "Boston, MA",
        "salary_range": {"min": 120000, "max": 160000},
        "experience_required": "MBA + 3-5 years",
        "required_skills": [
            "Technology Product Management", "Agile / Scrum Methodology",
            "Data Visualization", "SQL & Database Management",
            "Communication (Verbal)", "Cross-functional Collaboration",
        ],
        "preferred_skills": [
            "Python Programming", "Machine Learning Fundamentals",
            "A/B Testing & Experimentation", "UX/UI Design Principles",
        ],
        "description": "Drive product strategy and execution for enterprise SaaS platform",
    },
    {
        "title": "Strategy Consultant (Associate)",
        "company_type": "MBB Consulting",
        "industry": "Consulting",
        "location": "Boston, MA",
        "salary_range": {"min": 175000, "max": 200000},
        "experience_required": "MBA + 2-5 years pre-MBA",
        "required_skills": [
            "Management Consulting Frameworks", "Communication (Verbal)",
            "Communication (Written)", "Excel / Google Sheets (Advanced)",
            "Strategic Thinking", "Problem Solving",
        ],
        "preferred_skills": [
            "Data Visualization", "Python Programming",
            "Presentation Design", "Team Leadership",
        ],
        "description": "Advise Fortune 500 clients on strategic growth initiatives",
    },
    {
        "title": "Investment Banking Associate",
        "company_type": "Bulge Bracket Bank",
        "industry": "Financial Services",
        "location": "Boston, MA",
        "salary_range": {"min": 175000, "max": 200000},
        "experience_required": "MBA + 2-4 years pre-MBA",
        "required_skills": [
            "Financial Modeling", "Valuation Methods",
            "Mergers & Acquisitions Analysis", "Excel / Google Sheets (Advanced)",
            "Accounting (GAAP)", "Communication (Written)",
        ],
        "preferred_skills": [
            "Presentation Design", "Time Management",
            "Investment Banking",
        ],
        "description": "Execute M&A and capital markets transactions for corporate clients",
    },
    {
        "title": "Venture Capital Associate",
        "company_type": "VC Fund",
        "industry": "Financial Services",
        "location": "Cambridge, MA",
        "salary_range": {"min": 130000, "max": 175000},
        "experience_required": "MBA + 3-5 years in tech/startup",
        "required_skills": [
            "Venture Capital", "Financial Modeling",
            "Market Sizing (TAM/SAM/SOM)", "Due Diligence (Startup)",
            "Networking", "Unit Economics",
        ],
        "preferred_skills": [
            "Lean Startup Methodology", "Customer Discovery",
            "Technology Product Management", "Python Programming",
        ],
        "description": "Source, evaluate, and manage early-stage technology investments",
    },
    {
        "title": "Brand Manager",
        "company_type": "CPG (Fortune 500)",
        "industry": "Consumer Goods",
        "location": "Boston, MA",
        "salary_range": {"min": 110000, "max": 145000},
        "experience_required": "MBA + 2-4 years marketing",
        "required_skills": [
            "Marketing Strategy", "Market Research Methods",
            "Digital Marketing Analytics", "Communication (Written)",
            "Pricing Strategy Models", "Stakeholder Management",
        ],
        "preferred_skills": [
            "Social Media Analytics", "A/B Testing & Experimentation",
            "Growth Marketing", "Creative & Innovation",
        ],
        "description": "Lead brand strategy and P&L for major consumer brand portfolio",
    },
    {
        "title": "Senior Data Scientist",
        "company_type": "Tech Startup",
        "industry": "Technology",
        "location": "Boston, MA",
        "salary_range": {"min": 140000, "max": 185000},
        "experience_required": "MBA/MS + 3-5 years data science",
        "required_skills": [
            "Python Programming", "SQL & Database Management",
            "Machine Learning Fundamentals", "Statistical Analysis",
            "Data Visualization", "A/B Testing & Experimentation",
        ],
        "preferred_skills": [
            "Natural Language Processing", "Cloud Computing (AWS/Azure/GCP)",
            "Product Analytics", "Communication (Verbal)",
        ],
        "description": "Build ML models and analytics infrastructure for growth-stage startup",
    },
    {
        "title": "Healthcare Strategy Manager",
        "company_type": "Health System",
        "industry": "Healthcare",
        "location": "Boston, MA",
        "salary_range": {"min": 120000, "max": 155000},
        "experience_required": "MBA + 3-5 years healthcare",
        "required_skills": [
            "Healthcare Management", "Healthcare Economics",
            "Strategic Thinking", "Data Visualization",
            "Stakeholder Management", "Change Management",
        ],
        "preferred_skills": [
            "Regulatory Compliance", "Operations Strategy",
            "Statistical Analysis", "Communication (Verbal)",
        ],
        "description": "Drive strategic initiatives for major academic medical center",
    },
    {
        "title": "Private Equity Associate",
        "company_type": "Mid-Market PE",
        "industry": "Financial Services",
        "location": "Boston, MA",
        "salary_range": {"min": 175000, "max": 225000},
        "experience_required": "MBA + 2-4 years IB/consulting",
        "required_skills": [
            "Private Equity", "Financial Modeling",
            "Valuation Methods", "Mergers & Acquisitions Analysis",
            "Accounting (GAAP)", "Excel / Google Sheets (Advanced)",
        ],
        "preferred_skills": [
            "Analytical Reasoning", "Due Diligence (Startup)",
            "Operations Strategy",
        ],
        "description": "Source deals, perform due diligence, and support portfolio companies",
    },
    {
        "title": "Director of Operations",
        "company_type": "Growth-Stage Startup",
        "industry": "Technology",
        "location": "Boston, MA",
        "salary_range": {"min": 130000, "max": 170000},
        "experience_required": "MBA + 5-7 years operations",
        "required_skills": [
            "Operations Strategy", "Supply Chain Management",
            "Project Management Tools", "Team Leadership",
            "Problem Solving", "Agile / Scrum Methodology",
        ],
        "preferred_skills": [
            "Quality Management (Six Sigma)", "Python Programming",
            "Supply Chain Analytics", "Scaling Operations",
        ],
        "description": "Scale operations for Series B startup entering hyper-growth phase",
    },
    {
        "title": "Sustainability & ESG Manager",
        "company_type": "Asset Management",
        "industry": "Financial Services",
        "location": "Boston, MA",
        "salary_range": {"min": 115000, "max": 150000},
        "experience_required": "MBA + 3-5 years ESG/sustainability",
        "required_skills": [
            "Energy & Sustainability", "Social Impact Investing",
            "Impact Measurement", "Data Visualization",
            "Communication (Written)", "Regulatory Compliance",
        ],
        "preferred_skills": [
            "Financial Modeling", "Statistical Analysis",
            "Stakeholder Management",
        ],
        "description": "Lead ESG integration and sustainable investment strategy",
    },
    {
        "title": "Growth Marketing Manager",
        "company_type": "Tech Startup (Series A-B)",
        "industry": "Technology",
        "location": "Boston, MA",
        "salary_range": {"min": 115000, "max": 150000},
        "experience_required": "MBA + 2-4 years digital marketing",
        "required_skills": [
            "Growth Marketing", "Digital Marketing Analytics",
            "SEO / SEM", "A/B Testing & Experimentation",
            "Social Media Analytics", "Product Analytics",
        ],
        "preferred_skills": [
            "SQL & Database Management", "Python Programming",
            "Viral Loops & Referral Programs", "Growth Hacking",
        ],
        "description": "Own customer acquisition and activation for SaaS startup",
    },
    {
        "title": "FinTech Product Lead",
        "company_type": "FinTech Scale-up",
        "industry": "Financial Services",
        "location": "Boston, MA",
        "salary_range": {"min": 145000, "max": 185000},
        "experience_required": "MBA + 4-6 years fintech/banking",
        "required_skills": [
            "FinTech", "Technology Product Management",
            "Regulatory Compliance", "Agile / Scrum Methodology",
            "UX/UI Design Principles", "Strategic Thinking",
        ],
        "preferred_skills": [
            "Blockchain Fundamentals", "API Development",
            "Data Visualization", "Python Programming",
        ],
        "description": "Lead product development for payments and lending platform",
    },
]


def get_all_postings() -> list:
    """Return all curated job postings."""
    return MBA_JOB_POSTINGS


def get_postings_by_industry(industry: str) -> list:
    return [p for p in MBA_JOB_POSTINGS if p["industry"].lower() == industry.lower()]


def get_postings_by_skill(skill_name: str) -> list:
    return [
        p for p in MBA_JOB_POSTINGS
        if skill_name in p["required_skills"] or skill_name in p["preferred_skills"]
    ]


def get_skill_demand_summary() -> dict:
    """Aggregate skill demand across all postings."""
    demand = {}
    for posting in MBA_JOB_POSTINGS:
        for skill in posting["required_skills"]:
            demand.setdefault(skill, {"required": 0, "preferred": 0})
            demand[skill]["required"] += 1
        for skill in posting["preferred_skills"]:
            demand.setdefault(skill, {"required": 0, "preferred": 0})
            demand[skill]["preferred"] += 1

    ranked = sorted(demand.items(), key=lambda x: x[1]["required"] + x[1]["preferred"], reverse=True)
    return {skill: counts for skill, counts in ranked}


def scrape_all(output_path: str = None) -> dict:
    """Export all job postings data."""
    result = {
        "postings": MBA_JOB_POSTINGS,
        "skill_demand": get_skill_demand_summary(),
        "total_postings": len(MBA_JOB_POSTINGS),
        "industries": list({p["industry"] for p in MBA_JOB_POSTINGS}),
    }

    if output_path:
        Path(output_path).write_text(json.dumps(result, indent=2))
        print(f"  Saved job postings data to {output_path}")

    return result


if __name__ == "__main__":
    output = str(Path(__file__).parent.parent / "data" / "job_postings.json")
    Path(output).parent.mkdir(exist_ok=True)
    data = scrape_all(output_path=output)
    print(f"Compiled {data['total_postings']} job postings across {len(data['industries'])} industries")
    print("\nTop skills by demand:")
    for skill, counts in list(data["skill_demand"].items())[:10]:
        print(f"  {skill}: {counts['required']} required, {counts['preferred']} preferred")
