CREATE TABLE IF NOT EXISTS schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    short_name TEXT NOT NULL,
    location TEXT NOT NULL DEFAULT 'Boston, MA',
    school_type TEXT NOT NULL CHECK(school_type IN ('entrepreneurship', 'general', 'hybrid')),
    ranking_us_news INTEGER,
    ranking_entrepreneurship INTEGER,
    website_url TEXT,
    career_report_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name TEXT NOT NULL,
    degree_type TEXT NOT NULL DEFAULT 'MBA',
    concentration TEXT,
    duration_months INTEGER,
    format TEXT CHECK(format IN ('full-time', 'part-time', 'online', 'executive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    program_id INTEGER REFERENCES programs(id),
    report_year INTEGER NOT NULL,
    industry TEXT NOT NULL,
    job_function TEXT,
    company TEXT,
    job_title TEXT,
    median_salary INTEGER,
    mean_salary INTEGER,
    signing_bonus INTEGER,
    employment_rate_at_grad REAL,
    employment_rate_3mo REAL,
    employment_rate_6mo REAL,
    pct_of_class REAL,
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL CHECK(category IN ('technical', 'soft', 'domain', 'entrepreneurship')),
    subcategory TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT NOT NULL,
    industry TEXT NOT NULL,
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    importance_score INTEGER NOT NULL CHECK(importance_score BETWEEN 1 AND 5),
    frequency TEXT CHECK(frequency IN ('essential', 'common', 'nice-to-have')),
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transferable_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    from_context TEXT NOT NULL,
    to_context TEXT NOT NULL,
    relevance_score REAL NOT NULL CHECK(relevance_score BETWEEN 0.0 AND 1.0),
    mapping_rationale TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    program_id INTEGER REFERENCES programs(id),
    course_code TEXT,
    name TEXT NOT NULL,
    description TEXT,
    skills_taught TEXT, -- JSON array of skill IDs
    credits REAL DEFAULT 3.0,
    semester TEXT,
    is_elective BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    project_type TEXT CHECK(project_type IN ('capstone', 'consulting', 'startup', 'research', 'competition', 'independent')),
    skills_developed TEXT, -- JSON array of skill IDs
    industry_relevance TEXT, -- JSON array of industries
    difficulty TEXT CHECK(difficulty IN ('beginner', 'intermediate', 'advanced')),
    estimated_hours INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skill_synonyms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id INTEGER NOT NULL REFERENCES skills(id),
    synonym TEXT NOT NULL,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(skill_id, synonym)
);

CREATE TABLE IF NOT EXISTS student_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    name TEXT,
    email TEXT,
    resume_data TEXT,     -- JSON parsed resume
    linkedin_data TEXT,   -- JSON parsed LinkedIn
    transcript_data TEXT, -- JSON parsed transcript
    extracted_skills TEXT, -- JSON array of skill IDs
    analysis_result TEXT,  -- JSON full AI analysis
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_job_outcomes_school ON job_outcomes(school_id);
CREATE INDEX IF NOT EXISTS idx_job_outcomes_industry ON job_outcomes(industry);
CREATE INDEX IF NOT EXISTS idx_job_skills_title ON job_skills(job_title);
CREATE INDEX IF NOT EXISTS idx_job_skills_skill ON job_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_courses_school ON courses(school_id);
CREATE INDEX IF NOT EXISTS idx_skill_synonyms_skill ON skill_synonyms(skill_id);
CREATE INDEX IF NOT EXISTS idx_transferable_skills_skill ON transferable_skills(skill_id);
