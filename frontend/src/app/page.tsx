import Link from "next/link";

const FEATURES = [
  {
    title: "Upload & Parse",
    desc: "Upload your resume and LinkedIn profile PDF. Our AI extracts skills, experience, and education automatically.",
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
    ),
  },
  {
    title: "Transcript Integration",
    desc: "Connect your Workday student portal to automatically import your academic transcript, courses, and GPA.",
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
  {
    title: "AI Analysis",
    desc: "Get a comprehensive skills gap analysis, entrepreneurship readiness score, and career fit assessment.",
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
  },
  {
    title: "Personalized Recommendations",
    desc: "Receive tailored suggestions for courses, projects, and jobs based on your unique profile and goals.",
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
  },
];

const SCHOOLS = [
  "Babson (Olin)", "Harvard (HBS)", "MIT Sloan", "BC Carroll", "BU Questrom",
  "Northeastern", "Brandeis IBS", "Suffolk Sawyer", "Bentley", "Hult",
];

export default function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-[#006747] to-[#004d35] text-white py-20 px-4">
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-balance">
            Your MBA Career, <span className="text-green-300">Powered by Data</span>
          </h1>
          <p className="text-lg md:text-xl text-white/80 mb-8 max-w-2xl mx-auto">
            Upload your resume and LinkedIn profile. Get AI-powered skill gap analysis, course
            recommendations, and career matching across 10 Boston-area MBA programs.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/upload"
              className="px-8 py-3 bg-white text-[#006747] font-semibold rounded-lg shadow-lg hover:bg-green-50 transition-colors"
            >
              Get Started
            </Link>
            <Link
              href="/explore"
              className="px-8 py-3 bg-white/10 text-white font-semibold rounded-lg border border-white/30 hover:bg-white/20 transition-colors"
            >
              Explore Data
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-12">How It Works</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {FEATURES.map((f, i) => (
              <div key={f.title} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="w-12 h-12 rounded-lg bg-[#006747]/10 flex items-center justify-center text-[#006747] mb-4">
                  {f.icon}
                </div>
                <div className="text-xs font-semibold text-[#006747] mb-1">Step {i + 1}</div>
                <h3 className="font-semibold text-gray-900 mb-2">{f.title}</h3>
                <p className="text-sm text-gray-600">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Schools */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">10 Boston MBA Programs</h2>
          <p className="text-gray-500 mb-8">Comprehensive job outcome and skills data across top schools</p>
          <div className="flex flex-wrap justify-center gap-3">
            {SCHOOLS.map((s) => (
              <span key={s} className="px-4 py-2 bg-gray-100 rounded-full text-sm font-medium text-gray-700">
                {s}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { value: "200+", label: "Skills Tracked" },
              { value: "10", label: "MBA Programs" },
              { value: "50+", label: "Job Outcomes" },
              { value: "26+", label: "Courses Mapped" },
            ].map((s) => (
              <div key={s.label} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
                <div className="text-3xl font-bold text-[#006747] mb-1">{s.value}</div>
                <div className="text-sm text-gray-500">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white/60 py-8 px-4 text-center text-sm">
        <p>Babson MBA Career Intelligence Platform</p>
        <p className="mt-1">Data from O*NET, BLS, and public school employment reports</p>
      </footer>
    </div>
  );
}
