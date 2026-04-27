# Babson MBA Career Intelligence Platform

AI-powered career guidance platform for MBA students. Upload your resume and LinkedIn PDF, connect your academic transcript via Workday, and get personalized recommendations for courses, projects, and jobs based on skills gap analysis across 10 Boston-area MBA programs.

![Dashboard](https://img.shields.io/badge/Stack-FastAPI%20%2B%20Next.js-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)

## Features

- **Resume & LinkedIn Parsing** — Upload PDFs; the system extracts skills, experience, and education using PyMuPDF + Claude AI
- **Workday Integration** — Mock adapter simulates Workday Student API with 3 sample student profiles (swappable for real API)
- **AI Profile Analysis** — Claude-powered insights including strengths, development areas, career recommendations, and entrepreneurship readiness scoring
- **Skills Gap Analysis** — Compare your skills against 7 MBA career paths (Startup Founder, Consultant, PM, IB, VC, Marketing, Data Science)
- **Personalized Recommendations** — Courses, hands-on projects, and job matches tailored to your skill gaps
- **School Comparison** — Explore employment outcomes, salaries, and rankings across 10 Boston MBA programs
- **200+ Skills Taxonomy** — Normalized skills across technical, soft, domain, and entrepreneurship categories with synonym mapping

## Architecture

```
Next.js Frontend (Port 3000)
    │ API Proxy (/api/* → :8000)
    ▼
FastAPI Backend (Port 8000)
    ├── PDF Parsers (resume, LinkedIn, transcript)
    ├── AI Engine (Claude API for analysis + recommendations)
    ├── Skills Normalizer (fuzzy matching + synonym lookup)
    └── SQLite Database
         ├── 10 schools, 200+ skills, 49 job outcomes
         ├── 26 courses, 15 projects, 87 job-skill mappings
         └── Transferable skills + synonym mappings
```

## Schools Covered

| School | Known For |
|--------|-----------|
| Babson College (Olin) | Entrepreneurship (#1) |
| Harvard Business School | General management |
| MIT Sloan | Tech, analytics |
| Boston College (Carroll) | Finance, consulting |
| Boston University (Questrom) | Health, digital tech |
| Northeastern (D'Amore-McKim) | Experiential learning |
| Brandeis IBS | International business |
| Suffolk (Sawyer) | Accounting, finance |
| Bentley University | Finance, analytics |
| Hult International | Global business |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- (Optional) Anthropic API key for AI-powered analysis

### Backend

```bash
cd backend
pip install -r requirements.txt

# Optional: set your Anthropic API key for AI features
export ANTHROPIC_API_KEY=sk-ant-...

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000
```

The database is automatically created and seeded on first startup.

### Frontend

```bash
cd frontend
npm install
npm run build
npm start
# or for development:
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## User Flow

1. **Landing Page** (`/`) — Overview and "Get Started"
2. **Upload** (`/upload`) — Drag-drop resume and/or LinkedIn PDF
3. **Transcript** (`/transcript`) — Connect Workday (mock) to import academic data
4. **Dashboard** (`/dashboard`) — View skills inventory, entrepreneurship score, career fit radar, AI insights, and gap analysis
5. **Courses** (`/recommendations/courses`) — Personalized course recommendations
6. **Projects** (`/recommendations/projects`) — Hands-on project suggestions
7. **Jobs** (`/recommendations/jobs`) — Job matches with salary ranges and missing skills
8. **Explore** (`/explore`) — Compare outcomes across all 10 Boston MBA programs

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload/resume` | POST | Upload and parse resume PDF |
| `/api/upload/linkedin` | POST | Upload and parse LinkedIn PDF |
| `/api/workday/connect` | POST | Connect mock Workday transcript |
| `/api/workday/students` | GET | List available mock students |
| `/api/analyze/profile` | POST | Run AI profile analysis |
| `/api/recommend/courses` | GET | Get course recommendations |
| `/api/recommend/projects` | GET | Get project recommendations |
| `/api/recommend/jobs` | GET | Get job recommendations |
| `/api/data/outcomes/{school}` | GET | Employment outcomes by school |
| `/api/data/skills/taxonomy` | GET | Full skills taxonomy |
| `/api/data/skills/{industry}` | GET | Skills by industry |
| `/api/data/schools` | GET | List all schools |
| `/api/data/schools/compare` | GET | Compare schools side-by-side |
| `/api/data/compare` | POST | Compare student skills vs target role |

## Tech Stack

**Backend:** Python, FastAPI, SQLite, PyMuPDF, Anthropic Claude API

**Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Recharts

**Data Sources:** O*NET, BLS, curated school employment reports

## Project Structure

```
babson-career-platform/
├── backend/
│   ├── main.py                  # FastAPI app + all endpoints
│   ├── config.py                # Configuration
│   ├── database/
│   │   ├── schema.sql           # 10 tables
│   │   ├── connection.py        # SQLite helpers
│   │   └── seed_data.py         # Schools, skills, outcomes, courses, projects
│   ├── parsers/
│   │   ├── resume_parser.py     # Resume PDF → structured data
│   │   ├── linkedin_parser.py   # LinkedIn PDF → structured data
│   │   └── transcript_parser.py # Transcript parsing + Workday converter
│   ├── scrapers/
│   │   ├── onet_scraper.py      # O*NET occupation data
│   │   ├── bls_scraper.py       # BLS salary/outlook data
│   │   ├── school_outcomes.py   # Curated employment data
│   │   ├── job_postings.py      # Representative MBA job postings
│   │   └── skills_normalizer.py # Fuzzy matching + synonym resolution
│   ├── integrations/
│   │   └── workday_mock.py      # Mock Workday Student adapter
│   ├── ai/
│   │   ├── profile_analyzer.py  # Claude-powered profile analysis
│   │   └── recommender.py       # Course/project/job recommendations
│   └── requirements.txt
└── frontend/
    ├── package.json
    ├── next.config.mjs          # API proxy to backend
    ├── tailwind.config.ts
    └── src/
        ├── lib/
        │   ├── api.ts           # API client + TypeScript interfaces
        │   └── session.ts       # localStorage session management
        ├── components/
        │   ├── Navbar.tsx
        │   ├── FileUploader.tsx
        │   ├── SkillsRadar.tsx
        │   ├── GapAnalysis.tsx
        │   ├── RecommendationCard.tsx
        │   ├── SchoolComparison.tsx
        │   └── SkillsHeatmap.tsx
        └── app/
            ├── page.tsx                          # Landing
            ├── upload/page.tsx                   # PDF upload
            ├── transcript/page.tsx               # Workday connect
            ├── dashboard/page.tsx                # Analysis dashboard
            ├── recommendations/courses/page.tsx  # Course recs
            ├── recommendations/projects/page.tsx # Project recs
            ├── recommendations/jobs/page.tsx     # Job matches
            └── explore/page.tsx                  # School comparison
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | None | Enables AI-powered analysis (falls back to rule-based) |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` | Claude model to use |
| `WORKDAY_MODE` | `mock` | `mock` or `live` for Workday integration |
| `CORS_ORIGINS` | `localhost:3000` | Allowed CORS origins |

## License

MIT
