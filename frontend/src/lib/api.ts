const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...options?.headers },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function uploadResume(file: File, sessionId?: string) {
  const form = new FormData();
  form.append("file", file);
  const qs = sessionId ? `?session_id=${sessionId}` : "";
  return request<{
    session_id: string;
    parsed: { name: string; email: string; skills_count: number; experience_count: number; education_count: number };
  }>(`/api/upload/resume${qs}`, { method: "POST", body: form });
}

export async function uploadLinkedIn(file: File, sessionId?: string) {
  const form = new FormData();
  form.append("file", file);
  const qs = sessionId ? `?session_id=${sessionId}` : "";
  return request<{
    session_id: string;
    parsed: { name: string; headline: string; skills_count: number; experience_count: number };
  }>(`/api/upload/linkedin${qs}`, { method: "POST", body: form });
}

export async function connectWorkday(sessionId: string, studentId?: string) {
  return request<{
    session_id: string;
    student: { name: string; program: string; gpa: number; courses_count: number; credits_completed: number };
  }>("/api/workday/connect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, student_id: studentId }),
  });
}

export async function listMockStudents() {
  return request<{
    students: { student_id: string; name: string; program: string }[];
  }>("/api/workday/students");
}

export async function analyzeProfile(sessionId: string) {
  return request<{ session_id: string; analysis: Analysis }>("/api/analyze/profile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
}

export async function getCourseRecommendations(sessionId: string) {
  return request<{ recommendations: CourseRec[] }>(`/api/recommend/courses?session_id=${sessionId}`);
}

export async function getProjectRecommendations(sessionId: string) {
  return request<{ recommendations: ProjectRec[] }>(`/api/recommend/projects?session_id=${sessionId}`);
}

export async function getJobRecommendations(sessionId: string) {
  return request<{ recommendations: JobRec[] }>(`/api/recommend/jobs?session_id=${sessionId}`);
}

export async function getSchools() {
  return request<{ schools: School[] }>("/api/data/schools");
}

export async function getSchoolOutcomes(school: string) {
  return request<{ school: School; outcomes: Outcome[] }>(`/api/data/outcomes/${school}`);
}

export async function compareSchools(schools?: string) {
  const qs = schools ? `?schools=${schools}` : "";
  return request<{ comparison: SchoolComparison[] }>(`/api/data/schools/compare${qs}`);
}

export async function getSkillsTaxonomy() {
  return request<{ taxonomy: Record<string, Skill[]>; total: number }>("/api/data/skills/taxonomy");
}

export async function getSession(sessionId: string) {
  return request<{
    session_id: string;
    has_resume: boolean;
    has_linkedin: boolean;
    has_transcript: boolean;
    has_analysis: boolean;
  }>(`/api/session/${sessionId}`);
}

// Types
export interface Analysis {
  skills_inventory: Record<string, { name: string; subcategory: string }[]>;
  total_skills_identified: number;
  skill_evidence?: SkillEvidence[];
  entrepreneurship_readiness: {
    score: number;
    out_of: number;
    entrepreneurship_skills_count: number;
    interpretation: string;
    skills_present: string[];
    skills_missing: string[];
  };
  career_gap_analysis: CareerGap[];
  experience_summary: { total_roles: number; estimated_years_experience: number; roles: string[] };
  ai_insights: {
    strengths: string[];
    development_areas: string[];
    career_recommendations: string[];
    immediate_actions: string[];
    entrepreneurship_assessment: string;
  } | null;
  local_advisor?: {
    summary: string;
    strengths: string[];
    development_areas: string[];
    recommended_next_steps: string[];
    explanation_sources: { type: "skill" | "course" | "project" | "job" | "transcript"; label: string }[];
  } | null;
  intelligence?: {
    mode: "offline" | "online";
    provider: "ollama" | "azure" | "deterministic";
    model: string | null;
    embedding_model: string | null;
    fallback_used: boolean;
    health: "ok" | "degraded" | "unavailable";
    detail?: string;
  };
  performance?: {
    extraction_ms: number;
    embedding_ms: number;
    scoring_ms: number;
    advisor_ms: number;
    cached_embeddings_used: number;
  };
  transcript_summary: {
    gpa: number;
    credits_completed: number;
    credits_required: number;
    total_courses: number;
    top_courses: string[];
  } | null;
}

export interface CareerGap {
  career_path: string;
  industry: string;
  match_percentage: number;
  semantic_match_score?: number;
  combined_match_score?: number;
  priority_missing_skills?: string[];
  matching_skills: string[];
  missing_essential_skills: string[];
  missing_common_skills: string[];
  fit_level: string;
}

export interface SkillEvidence {
  skill: string;
  raw_skill?: string;
  evidence_text: string;
  source: "resume" | "linkedin" | "transcript";
  confidence: number;
  evidence_type: "explicit" | "inferred" | "course_mapped";
}

export interface CourseRec {
  name: string;
  school: string;
  course_code: string;
  description: string;
  credits: number;
  skills_taught: string[];
  gaps_addressed: string[];
  relevance_score: number;
  rationale: string;
  is_elective: boolean;
  semester: string;
}

export interface ProjectRec {
  title: string;
  description: string;
  project_type: string;
  difficulty: string;
  estimated_hours: number;
  skills_developed: string[];
  gaps_addressed: string[];
  relevance_score: number;
  rationale: string;
}

export interface JobRec {
  title: string;
  company_type: string;
  industry: string;
  location: string;
  salary_range: { min: number; max: number };
  experience_required: string;
  description: string;
  matching_skills: string[];
  missing_required_skills: string[];
  required_match_pct: number;
  total_match_pct: number;
  relevance_score: number;
  rationale: string;
}

export interface School {
  id: number;
  name: string;
  short_name: string;
  location: string;
  school_type: string;
  ranking_us_news: number;
  ranking_entrepreneurship: number | null;
}

export interface Outcome {
  industry: string;
  job_function: string;
  company: string;
  job_title: string;
  median_salary: number;
  mean_salary: number;
  employment_rate_6mo: number;
  pct_of_class: number;
}

export interface SchoolComparison {
  school: string;
  full_name: string;
  type: string;
  ranking_us_news: number;
  outcomes_by_industry: { industry: string; avg_salary: number; employment_rate: number }[];
}

export interface Skill {
  id: number;
  name: string;
  category: string;
  subcategory: string;
  description: string;
}
