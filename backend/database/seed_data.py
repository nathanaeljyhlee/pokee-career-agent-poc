"""Seed the database with baseline data for all 10 Boston MBA programs."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import init_db, execute, execute_many, get_connection

# ---------------------------------------------------------------------------
# Schools
# ---------------------------------------------------------------------------
SCHOOLS = [
    ("Babson College (Olin Graduate School)", "Babson", "Wellesley, MA", "entrepreneurship", 15, 1, "https://www.babson.edu/academics/graduate-school/", None),
    ("Harvard Business School", "HBS", "Boston, MA", "general", 1, 5, "https://www.hbs.edu/mba/", None),
    ("MIT Sloan School of Management", "MIT Sloan", "Cambridge, MA", "hybrid", 5, 2, "https://mitsloan.mit.edu/mba", None),
    ("Boston College (Carroll School of Management)", "BC Carroll", "Chestnut Hill, MA", "general", 45, None, "https://www.bc.edu/bc-web/schools/carroll-school.html", None),
    ("Boston University (Questrom School of Business)", "BU Questrom", "Boston, MA", "general", 42, None, "https://www.bu.edu/questrom/", None),
    ("Northeastern University (D'Amore-McKim)", "Northeastern", "Boston, MA", "general", 56, None, "https://damore-mckim.northeastern.edu/", None),
    ("Brandeis International Business School", "Brandeis IBS", "Waltham, MA", "general", 65, None, "https://www.brandeis.edu/global/", None),
    ("Suffolk University (Sawyer Business School)", "Suffolk Sawyer", "Boston, MA", "general", 120, None, "https://www.suffolk.edu/business", None),
    ("Bentley University", "Bentley", "Waltham, MA", "general", 80, None, "https://www.bentley.edu/graduate", None),
    ("Hult International Business School", "Hult", "Boston, MA", "hybrid", 90, 8, "https://www.hult.edu/", None),
]

# ---------------------------------------------------------------------------
# Programs (school_short_name -> programs list)
# ---------------------------------------------------------------------------
PROGRAMS = {
    "Babson": [
        ("Full-Time MBA", "MBA", None, 21, "full-time"),
        ("MBA - Entrepreneurship", "MBA", "Entrepreneurship", 21, "full-time"),
        ("MBA - Finance", "MBA", "Finance", 21, "full-time"),
        ("MBA - Marketing", "MBA", "Marketing", 21, "full-time"),
        ("Blended Learning MBA", "MBA", None, 24, "part-time"),
    ],
    "HBS": [
        ("MBA Program", "MBA", None, 24, "full-time"),
        ("MBA/MPP Joint Degree", "MBA", "Public Policy", 36, "full-time"),
    ],
    "MIT Sloan": [
        ("MBA Program", "MBA", None, 24, "full-time"),
        ("MBA - Entrepreneurship & Innovation", "MBA", "Entrepreneurship & Innovation", 24, "full-time"),
        ("MBA - Finance", "MBA", "Finance", 24, "full-time"),
    ],
    "BC Carroll": [
        ("Full-Time MBA", "MBA", None, 24, "full-time"),
        ("Part-Time MBA", "MBA", None, 36, "part-time"),
    ],
    "BU Questrom": [
        ("Full-Time MBA", "MBA", None, 24, "full-time"),
        ("MBA - Health Sector Management", "MBA", "Health Sector", 24, "full-time"),
        ("Part-Time MBA", "MBA", None, 36, "part-time"),
    ],
    "Northeastern": [
        ("Full-Time MBA", "MBA", None, 24, "full-time"),
        ("Part-Time MBA", "MBA", None, 36, "part-time"),
    ],
    "Brandeis IBS": [
        ("MBA Program", "MBA", None, 21, "full-time"),
        ("MBA - Finance", "MBA", "Finance", 21, "full-time"),
    ],
    "Suffolk Sawyer": [
        ("MBA Program", "MBA", None, 24, "full-time"),
        ("Part-Time MBA", "MBA", None, 36, "part-time"),
    ],
    "Bentley": [
        ("MBA Program", "MBA", None, 24, "full-time"),
        ("MBA - Marketing Analytics", "MBA", "Marketing Analytics", 24, "full-time"),
    ],
    "Hult": [
        ("Global One-Year MBA", "MBA", None, 12, "full-time"),
        ("MBA - Entrepreneurship", "MBA", "Entrepreneurship", 12, "full-time"),
    ],
}

# ---------------------------------------------------------------------------
# Skills Taxonomy (~200 skills across 4 categories)
# ---------------------------------------------------------------------------
SKILLS = [
    # Technical (50)
    ("Python Programming", "technical", "Programming", "General-purpose programming for data analysis, automation, and web development"),
    ("SQL & Database Management", "technical", "Data", "Querying, designing, and managing relational databases"),
    ("Financial Modeling", "technical", "Finance", "Building spreadsheet-based models for valuation and forecasting"),
    ("Data Visualization", "technical", "Data", "Creating charts, dashboards, and visual data stories"),
    ("Excel / Google Sheets (Advanced)", "technical", "Productivity", "Pivot tables, VLOOKUP, macros, complex formulas"),
    ("Statistical Analysis", "technical", "Data", "Hypothesis testing, regression, ANOVA, and statistical inference"),
    ("Machine Learning Fundamentals", "technical", "Data", "Supervised/unsupervised learning, model evaluation, feature engineering"),
    ("R Programming", "technical", "Programming", "Statistical computing and data analysis"),
    ("Tableau / Power BI", "technical", "Data", "Business intelligence and dashboard tools"),
    ("Digital Marketing Analytics", "technical", "Marketing", "Google Analytics, attribution modeling, A/B testing"),
    ("Accounting (GAAP)", "technical", "Finance", "Financial statements, journal entries, GAAP compliance"),
    ("Valuation Methods", "technical", "Finance", "DCF, comparable companies, precedent transactions"),
    ("Supply Chain Analytics", "technical", "Operations", "Demand forecasting, inventory optimization, logistics modeling"),
    ("Project Management Tools", "technical", "Operations", "Jira, Asana, MS Project, Trello"),
    ("CRM Systems (Salesforce)", "technical", "Marketing", "Customer relationship management and sales pipeline tools"),
    ("ERP Systems (SAP)", "technical", "Operations", "Enterprise resource planning for operations and finance"),
    ("Blockchain Fundamentals", "technical", "Technology", "Distributed ledger technology, smart contracts, DeFi basics"),
    ("Cloud Computing (AWS/Azure/GCP)", "technical", "Technology", "Cloud infrastructure, services, and deployment"),
    ("API Development", "technical", "Programming", "RESTful API design, integration, and documentation"),
    ("Web Development", "technical", "Programming", "HTML/CSS/JavaScript, frontend frameworks, responsive design"),
    ("Cybersecurity Basics", "technical", "Technology", "Information security, risk assessment, compliance"),
    ("UX/UI Design Principles", "technical", "Design", "User research, wireframing, prototyping, usability testing"),
    ("Agile / Scrum Methodology", "technical", "Operations", "Sprint planning, standups, retrospectives, Kanban"),
    ("Business Intelligence", "technical", "Data", "Data warehousing, ETL, reporting, OLAP"),
    ("Natural Language Processing", "technical", "Data", "Text mining, sentiment analysis, LLMs"),
    ("A/B Testing & Experimentation", "technical", "Data", "Designing and analyzing controlled experiments"),
    ("Robotic Process Automation", "technical", "Technology", "Automating repetitive business processes with bots"),
    ("Quantitative Risk Analysis", "technical", "Finance", "VaR, Monte Carlo simulation, stress testing"),
    ("Mergers & Acquisitions Analysis", "technical", "Finance", "Deal structuring, due diligence, synergy modeling"),
    ("Derivative Pricing", "technical", "Finance", "Options, futures, swaps, Black-Scholes"),
    ("Revenue Forecasting", "technical", "Finance", "Building top-down and bottom-up revenue models"),
    ("SEO / SEM", "technical", "Marketing", "Search engine optimization and paid search marketing"),
    ("Social Media Analytics", "technical", "Marketing", "Measuring engagement, reach, sentiment across platforms"),
    ("Product Analytics", "technical", "Data", "Funnel analysis, cohort analysis, retention metrics"),
    ("Pricing Strategy Models", "technical", "Marketing", "Price elasticity, competitive pricing, bundling"),
    ("Operations Research", "technical", "Operations", "Linear programming, optimization, simulation"),
    ("Quality Management (Six Sigma)", "technical", "Operations", "DMAIC, process improvement, lean manufacturing"),
    ("Real Estate Financial Analysis", "technical", "Finance", "Cap rates, IRR, cash-on-cash returns, pro forma"),
    ("Healthcare Economics", "technical", "Domain", "Cost-effectiveness analysis, payer models, reimbursement"),
    ("Regulatory Compliance", "technical", "Domain", "SOX, GDPR, HIPAA, SEC compliance frameworks"),
    ("Econometrics", "technical", "Data", "Causal inference, panel data, instrumental variables"),
    ("Presentation Design", "technical", "Productivity", "Slide design, data storytelling, executive presentations"),
    ("Technical Writing", "technical", "Productivity", "Documentation, proposals, white papers"),
    ("Contract Negotiation", "technical", "Domain", "Term sheets, SLAs, vendor agreements"),
    ("Intellectual Property Strategy", "technical", "Domain", "Patents, trademarks, licensing, IP portfolio management"),
    ("Tax Strategy", "technical", "Finance", "Corporate tax planning, transfer pricing, tax credits"),
    ("Treasury Management", "technical", "Finance", "Cash management, liquidity planning, FX hedging"),
    ("Market Research Methods", "technical", "Marketing", "Surveys, focus groups, conjoint analysis, ethnography"),
    ("Geospatial Analysis", "technical", "Data", "GIS, location analytics, spatial modeling"),
    ("AI Strategy & Governance", "technical", "Technology", "AI ethics, deployment strategy, governance frameworks"),

    # Soft / Leadership (50)
    ("Strategic Thinking", "soft", "Leadership", "Ability to see the big picture and develop long-term plans"),
    ("Communication (Verbal)", "soft", "Communication", "Clear, persuasive verbal communication in meetings and presentations"),
    ("Communication (Written)", "soft", "Communication", "Professional writing for emails, reports, and proposals"),
    ("Team Leadership", "soft", "Leadership", "Motivating and directing teams to achieve shared goals"),
    ("Cross-functional Collaboration", "soft", "Teamwork", "Working effectively across departments and disciplines"),
    ("Negotiation", "soft", "Communication", "Reaching mutually beneficial agreements in business contexts"),
    ("Conflict Resolution", "soft", "Teamwork", "Managing and resolving interpersonal and team disagreements"),
    ("Emotional Intelligence", "soft", "Leadership", "Self-awareness, empathy, and managing relationships"),
    ("Critical Thinking", "soft", "Analytical", "Evaluating information objectively and making reasoned judgments"),
    ("Problem Solving", "soft", "Analytical", "Identifying root causes and developing effective solutions"),
    ("Decision Making Under Uncertainty", "soft", "Analytical", "Making sound decisions with incomplete information"),
    ("Stakeholder Management", "soft", "Leadership", "Managing expectations and relationships with key stakeholders"),
    ("Change Management", "soft", "Leadership", "Leading organizational change and overcoming resistance"),
    ("Mentoring & Coaching", "soft", "Leadership", "Developing others through guidance and feedback"),
    ("Public Speaking", "soft", "Communication", "Delivering compelling presentations to large audiences"),
    ("Active Listening", "soft", "Communication", "Fully understanding others before responding"),
    ("Networking", "soft", "Communication", "Building and maintaining professional relationships"),
    ("Time Management", "soft", "Productivity", "Prioritizing tasks and managing deadlines effectively"),
    ("Adaptability", "soft", "Resilience", "Adjusting to new situations and changing requirements"),
    ("Resilience", "soft", "Resilience", "Recovering from setbacks and maintaining performance under pressure"),
    ("Growth Mindset", "soft", "Resilience", "Embracing challenges and learning from failure"),
    ("Cultural Competence", "soft", "Global", "Working effectively with people from diverse cultural backgrounds"),
    ("Global Perspective", "soft", "Global", "Understanding international markets, geopolitics, and global business"),
    ("Ethics & Integrity", "soft", "Leadership", "Maintaining ethical standards and corporate responsibility"),
    ("Persuasion & Influence", "soft", "Communication", "Convincing others to adopt ideas or take action"),
    ("Creativity & Innovation", "soft", "Analytical", "Generating novel ideas and unconventional solutions"),
    ("Analytical Reasoning", "soft", "Analytical", "Breaking complex problems into components and reasoning systematically"),
    ("Delegation", "soft", "Leadership", "Assigning tasks effectively based on team strengths"),
    ("Executive Presence", "soft", "Leadership", "Projecting confidence and authority in senior settings"),
    ("Storytelling (Business)", "soft", "Communication", "Using narrative to convey data and strategy"),
    ("Self-motivation", "soft", "Resilience", "Driving own work without external pressure"),
    ("Curiosity", "soft", "Resilience", "Seeking to understand new domains and asking probing questions"),
    ("Feedback (Giving & Receiving)", "soft", "Teamwork", "Constructively giving and accepting feedback"),
    ("Consensus Building", "soft", "Teamwork", "Bringing diverse viewpoints to agreement"),
    ("Project Leadership", "soft", "Leadership", "Leading projects from initiation to delivery"),
    ("Board Communication", "soft", "Communication", "Communicating with boards of directors and advisory boards"),
    ("Investor Relations", "soft", "Communication", "Managing relationships with current and potential investors"),
    ("Crisis Management", "soft", "Leadership", "Leading organizations through unexpected crises"),
    ("Visionary Thinking", "soft", "Leadership", "Articulating a compelling future state and rallying teams around it"),
    ("Empowerment", "soft", "Leadership", "Creating environments where team members take ownership"),
    ("Client Relationship Management", "soft", "Communication", "Building and maintaining trust with clients"),
    ("Facilitation", "soft", "Teamwork", "Guiding group discussions to productive outcomes"),
    ("Influence Without Authority", "soft", "Leadership", "Leading when you don't have direct power"),
    ("Self-awareness", "soft", "Resilience", "Understanding own strengths, weaknesses, and biases"),
    ("Work-life Integration", "soft", "Resilience", "Managing demanding careers alongside personal life"),
    ("Political Savvy", "soft", "Leadership", "Navigating organizational politics effectively"),
    ("Coaching Conversations", "soft", "Leadership", "Structured coaching for direct reports and peers"),
    ("Inclusive Leadership", "soft", "Leadership", "Leading with awareness of DEI and psychological safety"),
    ("Ambiguity Tolerance", "soft", "Resilience", "Performing well when path forward is unclear"),
    ("Systems Thinking", "soft", "Analytical", "Understanding interconnected systems and feedback loops"),

    # Domain (50)
    ("Corporate Strategy", "domain", "Strategy", "Competitive positioning, growth strategy, diversification"),
    ("Management Consulting Frameworks", "domain", "Consulting", "Case frameworks, MECE, hypothesis-driven problem solving"),
    ("Private Equity", "domain", "Finance", "Fund structure, deal sourcing, portfolio management, exits"),
    ("Venture Capital", "domain", "Finance", "Startup evaluation, term sheets, portfolio construction"),
    ("Investment Banking", "domain", "Finance", "IPOs, M&A advisory, debt/equity capital markets"),
    ("Consumer Packaged Goods (CPG)", "domain", "Industry", "Brand management, retail strategy, product lifecycle"),
    ("Healthcare Management", "domain", "Industry", "Hospital operations, pharma, digital health, payer systems"),
    ("Technology Product Management", "domain", "Technology", "Roadmapping, feature prioritization, go-to-market"),
    ("Real Estate Development", "domain", "Industry", "Site selection, zoning, development finance, asset management"),
    ("Energy & Sustainability", "domain", "Industry", "Renewable energy, ESG, carbon markets, cleantech"),
    ("Nonprofit Management", "domain", "Industry", "Fundraising, governance, impact measurement, grant writing"),
    ("Government & Public Policy", "domain", "Industry", "Regulatory analysis, policy development, public-private partnerships"),
    ("Media & Entertainment", "domain", "Industry", "Content strategy, distribution, monetization, streaming economics"),
    ("Retail & E-commerce", "domain", "Industry", "Omnichannel strategy, inventory management, customer experience"),
    ("Manufacturing & Operations", "domain", "Industry", "Lean manufacturing, quality control, supply chain"),
    ("Financial Services", "domain", "Industry", "Banking, insurance, wealth management, fintech"),
    ("Pharmaceuticals & Biotech", "domain", "Industry", "Drug development pipeline, FDA approval process, commercialization"),
    ("Education Technology", "domain", "Industry", "EdTech platforms, curriculum design, learning analytics"),
    ("Aerospace & Defense", "domain", "Industry", "Defense contracting, aviation management, space tech"),
    ("Luxury & Fashion", "domain", "Industry", "Brand positioning, luxury retail, fashion supply chain"),
    ("Sports Management", "domain", "Industry", "Franchise operations, sponsorships, player management"),
    ("Food & Agriculture", "domain", "Industry", "Agtech, food safety, sustainable agriculture, distribution"),
    ("Social Impact Investing", "domain", "Finance", "Impact measurement, ESG integration, blended finance"),
    ("Corporate Development", "domain", "Strategy", "M&A strategy, partnerships, strategic alliances"),
    ("Business Development", "domain", "Strategy", "Pipeline management, partnership creation, market entry"),
    ("Marketing Strategy", "domain", "Marketing", "Brand positioning, go-to-market, competitive analysis"),
    ("Product Marketing", "domain", "Marketing", "Positioning, messaging, launch strategy, competitive intelligence"),
    ("Growth Marketing", "domain", "Marketing", "Acquisition, activation, retention, referral, revenue (AARRR)"),
    ("Sales Strategy", "domain", "Marketing", "Sales process design, territory planning, quota setting"),
    ("Human Capital Management", "domain", "HR", "Talent acquisition, development, retention, organizational design"),
    ("Organizational Behavior", "domain", "HR", "Team dynamics, motivation, culture, organizational change"),
    ("Compensation & Benefits", "domain", "HR", "Total rewards design, equity compensation, benchmarking"),
    ("International Trade", "domain", "Global", "Import/export regulations, tariffs, trade agreements"),
    ("Emerging Markets Strategy", "domain", "Global", "Market entry in developing economies, institutional voids"),
    ("Family Business Management", "domain", "Entrepreneurship", "Succession planning, governance, family dynamics"),
    ("Franchise Operations", "domain", "Entrepreneurship", "Franchise model design, franchisee management, scaling"),
    ("Corporate Innovation", "domain", "Strategy", "Intrapreneurship, innovation labs, corporate venturing"),
    ("Digital Transformation", "domain", "Technology", "Legacy modernization, digital strategy, change management"),
    ("Platform Business Models", "domain", "Technology", "Marketplace design, network effects, platform economics"),
    ("SaaS Business Models", "domain", "Technology", "Recurring revenue, churn management, unit economics"),
    ("Cybersecurity Management", "domain", "Technology", "InfoSec strategy, risk frameworks, incident response"),
    ("Data Governance", "domain", "Technology", "Data quality, privacy, compliance, data strategy"),
    ("FinTech", "domain", "Technology", "Payments, lending, insurtech, embedded finance"),
    ("PropTech", "domain", "Technology", "Real estate technology, smart buildings, marketplace platforms"),
    ("HealthTech", "domain", "Technology", "Telemedicine, EHR, digital therapeutics, health AI"),
    ("CleanTech", "domain", "Technology", "Green energy tech, carbon capture, circular economy"),
    ("EdTech", "domain", "Technology", "Learning platforms, adaptive learning, credentialing"),
    ("Supply Chain Management", "domain", "Operations", "Global sourcing, logistics, supplier relationships"),
    ("Operations Strategy", "domain", "Operations", "Capacity planning, process design, operational excellence"),
    ("Procurement & Sourcing", "domain", "Operations", "Vendor selection, contract management, cost reduction"),

    # Entrepreneurship (50)
    ("Business Model Canvas", "entrepreneurship", "Frameworks", "Mapping and iterating on 9 key business model components"),
    ("Lean Startup Methodology", "entrepreneurship", "Frameworks", "Build-measure-learn cycles, MVP, validated learning"),
    ("Customer Discovery", "entrepreneurship", "Validation", "Interviewing potential customers to validate assumptions"),
    ("Pitching & Storytelling", "entrepreneurship", "Communication", "Delivering compelling pitches to investors and stakeholders"),
    ("Fundraising Strategy", "entrepreneurship", "Finance", "Seed, Series A/B/C strategy, investor targeting, term negotiation"),
    ("Bootstrapping", "entrepreneurship", "Finance", "Growing a business with minimal external funding"),
    ("Minimum Viable Product (MVP) Design", "entrepreneurship", "Product", "Designing the simplest product to test core hypotheses"),
    ("Market Sizing (TAM/SAM/SOM)", "entrepreneurship", "Validation", "Estimating total, serviceable, and obtainable market sizes"),
    ("Competitive Analysis", "entrepreneurship", "Strategy", "Mapping competitors, identifying moats, positioning"),
    ("Unit Economics", "entrepreneurship", "Finance", "CAC, LTV, gross margin, contribution margin, payback period"),
    ("Cap Table Management", "entrepreneurship", "Finance", "Equity allocation, dilution modeling, option pools"),
    ("Venture Financing", "entrepreneurship", "Finance", "Convertible notes, SAFEs, priced rounds, down rounds"),
    ("Product-Market Fit", "entrepreneurship", "Validation", "Measuring and achieving strong demand-supply match"),
    ("Growth Hacking", "entrepreneurship", "Growth", "Low-cost, creative strategies for rapid user acquisition"),
    ("Viral Loops & Referral Programs", "entrepreneurship", "Growth", "Designing self-reinforcing growth mechanisms"),
    ("Pivot Strategy", "entrepreneurship", "Strategy", "Recognizing when and how to change direction"),
    ("Startup Financial Projections", "entrepreneurship", "Finance", "3-5 year financial models for early-stage companies"),
    ("Legal Entity Formation", "entrepreneurship", "Legal", "LLC, C-Corp, S-Corp, B-Corp formation and implications"),
    ("Intellectual Property Protection", "entrepreneurship", "Legal", "Patents, trademarks, trade secrets for startups"),
    ("Co-founder Dynamics", "entrepreneurship", "Team", "Choosing co-founders, splitting equity, managing disagreements"),
    ("Startup Team Building", "entrepreneurship", "Team", "Early hiring, culture setting, talent retention at scale"),
    ("Advisory Board Formation", "entrepreneurship", "Team", "Selecting advisors, structuring compensation, managing relationships"),
    ("Customer Development", "entrepreneurship", "Validation", "Systematic approach to understanding customer needs"),
    ("Design Thinking", "entrepreneurship", "Frameworks", "Empathize, define, ideate, prototype, test"),
    ("Rapid Prototyping", "entrepreneurship", "Product", "Quickly building functional prototypes for testing"),
    ("Go-to-Market Strategy", "entrepreneurship", "Strategy", "Launch planning, channel strategy, initial customer acquisition"),
    ("Sales in Early-Stage Startups", "entrepreneurship", "Growth", "Founder-led sales, first 10 customers, sales process design"),
    ("Community Building", "entrepreneurship", "Growth", "Building user communities for engagement and retention"),
    ("Crowdfunding", "entrepreneurship", "Finance", "Kickstarter, Indiegogo, equity crowdfunding strategies"),
    ("Social Enterprise Models", "entrepreneurship", "Impact", "Balancing profit and purpose, B-Corp certification"),
    ("Impact Measurement", "entrepreneurship", "Impact", "Defining and tracking social/environmental impact metrics"),
    ("Scaling Operations", "entrepreneurship", "Growth", "Transitioning from startup to scaleup, operational processes"),
    ("International Expansion", "entrepreneurship", "Growth", "Entering new markets, localization, regulatory compliance"),
    ("Exit Strategy", "entrepreneurship", "Strategy", "IPO preparation, M&A positioning, secondary sales"),
    ("Due Diligence (Startup)", "entrepreneurship", "Finance", "Preparing for and conducting investor due diligence"),
    ("Startup Accounting", "entrepreneurship", "Finance", "Burn rate, runway, accrual vs cash basis, SaaS metrics"),
    ("Venture Studio Model", "entrepreneurship", "Frameworks", "Building multiple startups within a studio framework"),
    ("Corporate Venturing", "entrepreneurship", "Strategy", "Corporate venture arms, strategic investments, spin-offs"),
    ("Incubator / Accelerator Programs", "entrepreneurship", "Ecosystem", "YC, Techstars, MassChallenge, program selection"),
    ("Startup Ecosystem Navigation", "entrepreneurship", "Ecosystem", "Understanding the Boston/Cambridge startup ecosystem"),
    ("Technology Transfer", "entrepreneurship", "Ecosystem", "Commercializing university research and patents"),
    ("Regulatory Strategy for Startups", "entrepreneurship", "Legal", "Navigating regulations in fintech, healthtech, etc."),
    ("Freemium & Pricing Strategy", "entrepreneurship", "Product", "Designing pricing tiers, conversion optimization"),
    ("Customer Retention Strategies", "entrepreneurship", "Growth", "Reducing churn, increasing engagement, NPS"),
    ("Marketplace Design", "entrepreneurship", "Product", "Two-sided marketplace creation, chicken-and-egg problem"),
    ("Hardware Startup Essentials", "entrepreneurship", "Product", "Prototyping, manufacturing, supply chain for physical products"),
    ("Subscription Business Models", "entrepreneurship", "Product", "MRR/ARR, churn, expansion revenue, pricing"),
    ("Venture Debt", "entrepreneurship", "Finance", "Non-dilutive financing, loan structures, covenants"),
    ("Startup PR & Media Relations", "entrepreneurship", "Growth", "Press outreach, thought leadership, brand building"),
    ("Founder Mental Health & Wellness", "entrepreneurship", "Team", "Managing stress, burnout prevention, support systems"),
]

# ---------------------------------------------------------------------------
# Skill Synonyms (canonical_name -> list of synonyms)
# ---------------------------------------------------------------------------
SKILL_SYNONYMS = {
    "Python Programming": ["Python", "Python 3", "Python coding", "Python scripting"],
    "SQL & Database Management": ["SQL", "MySQL", "PostgreSQL", "Database design", "RDBMS"],
    "Financial Modeling": ["Financial modelling", "DCF modeling", "Spreadsheet modeling", "Excel modeling"],
    "Data Visualization": ["Data viz", "Dashboard design", "Chart design", "Visual analytics"],
    "Machine Learning Fundamentals": ["ML", "Machine learning", "Predictive modeling", "AI/ML"],
    "Communication (Verbal)": ["Oral communication", "Verbal skills", "Speaking skills", "Presentation skills"],
    "Communication (Written)": ["Written communication", "Business writing", "Professional writing"],
    "Team Leadership": ["Team management", "Leading teams", "Team lead"],
    "Negotiation": ["Negotiation skills", "Deal negotiation", "Contract negotiation"],
    "Business Model Canvas": ["BMC", "Osterwalder canvas", "Business model design"],
    "Lean Startup Methodology": ["Lean startup", "Build-measure-learn", "Lean methodology"],
    "Customer Discovery": ["Custdev", "Customer interviews", "Discovery interviews"],
    "Pitching & Storytelling": ["Pitch deck", "Investor pitch", "Startup pitch", "Elevator pitch"],
    "Unit Economics": ["Unit econ", "CAC/LTV", "Customer economics"],
    "Venture Capital": ["VC", "Venture investing", "VC investing"],
    "Private Equity": ["PE", "Buyout", "LBO", "Leveraged buyout"],
    "Management Consulting Frameworks": ["Case interview", "Consulting frameworks", "MECE", "Hypothesis-driven"],
    "Digital Marketing Analytics": ["Digital analytics", "Web analytics", "Marketing analytics"],
    "Strategic Thinking": ["Strategic planning", "Strategy development", "Long-term planning"],
    "Corporate Strategy": ["Business strategy", "Corporate planning", "Strategic management"],
}

# ---------------------------------------------------------------------------
# Transferable Skills Mappings
# ---------------------------------------------------------------------------
TRANSFERABLE_MAPPINGS = [
    ("Financial Modeling", "Consulting", "Startup Finance", 0.85, "Financial modeling in consulting translates to startup financial projections"),
    ("Financial Modeling", "Investment Banking", "Venture Capital", 0.90, "IB valuation skills directly applicable to VC deal evaluation"),
    ("Team Leadership", "Corporate Management", "Startup Founding", 0.75, "Corporate leadership translates but startup context requires more ambiguity tolerance"),
    ("Strategic Thinking", "Consulting", "Entrepreneurship", 0.80, "Strategy consulting frameworks adaptable to startup strategy"),
    ("Communication (Verbal)", "Sales", "Fundraising", 0.85, "Sales presentation skills transfer well to investor pitching"),
    ("Project Management Tools", "Corporate IT", "Startup Operations", 0.70, "PM tools useful but startups need more flexibility"),
    ("Data Visualization", "Business Intelligence", "Product Management", 0.80, "BI dashboarding translates to product analytics"),
    ("Negotiation", "Procurement", "Venture Financing", 0.75, "Procurement negotiation translates to term sheet negotiation"),
    ("Machine Learning Fundamentals", "Data Science", "AI Product Development", 0.85, "ML knowledge transfers directly to building AI products"),
    ("CRM Systems (Salesforce)", "Enterprise Sales", "Startup Sales", 0.65, "CRM experience helpful but startups often use simpler tools"),
    ("Critical Thinking", "Academic Research", "Business Strategy", 0.80, "Research methodology translates to strategic analysis"),
    ("Problem Solving", "Engineering", "Management Consulting", 0.85, "Engineering problem-solving maps well to case-based consulting"),
    ("Growth Hacking", "Digital Marketing", "Product Management", 0.75, "Growth marketing skills overlap with product-led growth"),
    ("Customer Discovery", "Market Research", "Product Development", 0.90, "Customer research directly informs product decisions"),
    ("Pitching & Storytelling", "Sales", "Corporate Leadership", 0.80, "Storytelling for customers transfers to executive communication"),
]

# ---------------------------------------------------------------------------
# Job Outcomes (representative data per school)
# ---------------------------------------------------------------------------
JOB_OUTCOMES = [
    # Babson
    ("Babson", 2024, "Technology", "Product Management", "Google", "Product Manager", 155000, 165000, 30000, 0.82, 0.91, 0.95, 0.18),
    ("Babson", 2024, "Entrepreneurship", "Founder/CEO", None, "Founder", None, None, None, 0.82, 0.91, 0.95, 0.22),
    ("Babson", 2024, "Consulting", "Strategy Consulting", "Bain & Company", "Associate Consultant", 175000, 178000, 35000, 0.82, 0.91, 0.95, 0.15),
    ("Babson", 2024, "Financial Services", "Venture Capital", None, "Associate", 140000, 145000, 25000, 0.82, 0.91, 0.95, 0.10),
    ("Babson", 2024, "Consumer Goods", "Marketing", "Procter & Gamble", "Brand Manager", 125000, 130000, 20000, 0.82, 0.91, 0.95, 0.08),
    ("Babson", 2024, "Healthcare", "Operations", "Mass General Brigham", "Operations Analyst", 115000, 120000, 15000, 0.82, 0.91, 0.95, 0.07),
    ("Babson", 2024, "Real Estate", "Development", None, "Analyst", 120000, 125000, 20000, 0.82, 0.91, 0.95, 0.05),
    ("Babson", 2024, "Nonprofit", "Social Enterprise", None, "Program Director", 95000, 100000, None, 0.82, 0.91, 0.95, 0.04),
    ("Babson", 2024, "Financial Services", "Investment Management", "Fidelity", "Analyst", 135000, 140000, 25000, 0.82, 0.91, 0.95, 0.06),
    ("Babson", 2024, "Technology", "Software/Data", "Amazon", "Sr. Business Analyst", 145000, 150000, 28000, 0.82, 0.91, 0.95, 0.05),

    # HBS
    ("HBS", 2024, "Consulting", "Strategy Consulting", "McKinsey & Company", "Associate", 195000, 200000, 35000, 0.90, 0.96, 0.98, 0.25),
    ("HBS", 2024, "Financial Services", "Private Equity", "KKR", "Associate", 200000, 210000, 40000, 0.90, 0.96, 0.98, 0.15),
    ("HBS", 2024, "Technology", "Product Management", "Meta", "Product Manager", 180000, 190000, 35000, 0.90, 0.96, 0.98, 0.18),
    ("HBS", 2024, "Financial Services", "Investment Banking", "Goldman Sachs", "Associate", 185000, 195000, 35000, 0.90, 0.96, 0.98, 0.10),
    ("HBS", 2024, "Entrepreneurship", "Founder/CEO", None, "Founder", None, None, None, 0.90, 0.96, 0.98, 0.12),
    ("HBS", 2024, "Technology", "General Management", "Amazon", "Senior Manager", 175000, 185000, 30000, 0.90, 0.96, 0.98, 0.08),
    ("HBS", 2024, "Healthcare", "Pharma/Biotech", "Pfizer", "Strategy Manager", 170000, 175000, 30000, 0.90, 0.96, 0.98, 0.05),
    ("HBS", 2024, "Nonprofit", "Social Enterprise", None, "Executive Director", 120000, 130000, None, 0.90, 0.96, 0.98, 0.03),

    # MIT Sloan
    ("MIT Sloan", 2024, "Technology", "Product Management", "Apple", "Product Manager", 175000, 185000, 35000, 0.88, 0.94, 0.97, 0.22),
    ("MIT Sloan", 2024, "Consulting", "Strategy Consulting", "BCG", "Consultant", 190000, 195000, 35000, 0.88, 0.94, 0.97, 0.20),
    ("MIT Sloan", 2024, "Technology", "Data/Analytics", "Google", "Data Scientist", 170000, 180000, 30000, 0.88, 0.94, 0.97, 0.12),
    ("MIT Sloan", 2024, "Entrepreneurship", "Founder/CEO", None, "Founder", None, None, None, 0.88, 0.94, 0.97, 0.15),
    ("MIT Sloan", 2024, "Financial Services", "FinTech", "Stripe", "Strategy Lead", 165000, 175000, 30000, 0.88, 0.94, 0.97, 0.08),
    ("MIT Sloan", 2024, "Energy & Sustainability", "CleanTech", None, "VP Operations", 155000, 165000, 25000, 0.88, 0.94, 0.97, 0.06),

    # BC Carroll
    ("BC Carroll", 2024, "Financial Services", "Investment Management", "State Street", "Analyst", 130000, 135000, 20000, 0.78, 0.88, 0.93, 0.25),
    ("BC Carroll", 2024, "Consulting", "Management Consulting", "Deloitte", "Consultant", 160000, 165000, 30000, 0.78, 0.88, 0.93, 0.20),
    ("BC Carroll", 2024, "Technology", "IT Management", "Wayfair", "Program Manager", 140000, 145000, 20000, 0.78, 0.88, 0.93, 0.12),
    ("BC Carroll", 2024, "Consumer Goods", "Marketing", "Hasbro", "Marketing Manager", 120000, 125000, 15000, 0.78, 0.88, 0.93, 0.10),

    # BU Questrom
    ("BU Questrom", 2024, "Healthcare", "Health Sector Management", "CVS Health", "Strategy Analyst", 125000, 130000, 20000, 0.76, 0.86, 0.92, 0.18),
    ("BU Questrom", 2024, "Consulting", "Management Consulting", "EY-Parthenon", "Consultant", 155000, 160000, 28000, 0.76, 0.86, 0.92, 0.15),
    ("BU Questrom", 2024, "Technology", "Digital Strategy", "HubSpot", "Product Strategist", 140000, 145000, 22000, 0.76, 0.86, 0.92, 0.12),
    ("BU Questrom", 2024, "Financial Services", "Banking", "Citizens Bank", "VP", 135000, 140000, 20000, 0.76, 0.86, 0.92, 0.10),

    # Northeastern
    ("Northeastern", 2024, "Technology", "Product/Program Management", "Wayfair", "Senior PM", 135000, 140000, 18000, 0.74, 0.85, 0.91, 0.20),
    ("Northeastern", 2024, "Consulting", "Operations Consulting", "Accenture", "Manager", 150000, 155000, 25000, 0.74, 0.85, 0.91, 0.15),
    ("Northeastern", 2024, "Healthcare", "Health IT", "Athenahealth", "Director", 130000, 135000, 18000, 0.74, 0.85, 0.91, 0.10),
    ("Northeastern", 2024, "Financial Services", "FinTech", "Fidelity", "Analyst", 125000, 130000, 15000, 0.74, 0.85, 0.91, 0.12),

    # Brandeis IBS
    ("Brandeis IBS", 2024, "Financial Services", "Asset Management", "Wellington Management", "Analyst", 125000, 130000, 18000, 0.72, 0.83, 0.90, 0.30),
    ("Brandeis IBS", 2024, "Financial Services", "Banking", "Bank of America", "Associate", 120000, 125000, 18000, 0.72, 0.83, 0.90, 0.20),
    ("Brandeis IBS", 2024, "Consulting", "Consulting", "Capgemini", "Consultant", 140000, 145000, 22000, 0.72, 0.83, 0.90, 0.12),

    # Suffolk Sawyer
    ("Suffolk Sawyer", 2024, "Financial Services", "Accounting", "PwC", "Senior Associate", 110000, 115000, 12000, 0.70, 0.80, 0.88, 0.25),
    ("Suffolk Sawyer", 2024, "Financial Services", "Banking", "Eastern Bank", "Analyst", 100000, 105000, 10000, 0.70, 0.80, 0.88, 0.20),
    ("Suffolk Sawyer", 2024, "Technology", "IT Management", None, "IT Manager", 105000, 110000, 12000, 0.70, 0.80, 0.88, 0.12),

    # Bentley
    ("Bentley", 2024, "Financial Services", "Financial Analysis", "Fidelity", "Senior Analyst", 125000, 130000, 18000, 0.75, 0.85, 0.92, 0.25),
    ("Bentley", 2024, "Technology", "Business Analytics", "Liberty Mutual", "Analytics Manager", 130000, 135000, 18000, 0.75, 0.85, 0.92, 0.15),
    ("Bentley", 2024, "Consulting", "IT Consulting", "Deloitte", "Consultant", 150000, 155000, 25000, 0.75, 0.85, 0.92, 0.12),

    # Hult
    ("Hult", 2024, "Entrepreneurship", "Founder/CEO", None, "Founder", None, None, None, 0.68, 0.78, 0.85, 0.20),
    ("Hult", 2024, "Technology", "Digital Marketing", None, "Marketing Director", 110000, 115000, 12000, 0.68, 0.78, 0.85, 0.15),
    ("Hult", 2024, "Consulting", "Strategy", None, "Strategy Analyst", 120000, 125000, 15000, 0.68, 0.78, 0.85, 0.12),
    ("Hult", 2024, "Consumer Goods", "International Business", None, "Business Dev Manager", 105000, 110000, 10000, 0.68, 0.78, 0.85, 0.10),
]

# ---------------------------------------------------------------------------
# Courses (sample Babson + cross-school courses)
# ---------------------------------------------------------------------------
COURSES_DATA = [
    # Babson courses
    ("Babson", None, "ENT6200", "Entrepreneurial Thought and Action", "Babson's signature course on ETA methodology", '["Business Model Canvas", "Lean Startup Methodology", "Customer Discovery", "Pitching & Storytelling"]', 3.0, "Fall/Spring", False),
    ("Babson", None, "FIN7200", "Corporate Financial Management", "Advanced corporate finance, valuation, capital structure", '["Financial Modeling", "Valuation Methods", "Revenue Forecasting"]', 3.0, "Fall", False),
    ("Babson", None, "MKT7400", "Marketing Management", "Marketing strategy, consumer behavior, market research", '["Marketing Strategy", "Market Research Methods", "Digital Marketing Analytics"]', 3.0, "Fall", False),
    ("Babson", None, "OPM7100", "Operations Management", "Process design, supply chain, quality management", '["Supply Chain Analytics", "Operations Strategy", "Quality Management (Six Sigma)"]', 3.0, "Spring", False),
    ("Babson", None, "MOB7200", "Leading and Managing People", "Organizational behavior, team leadership, change management", '["Team Leadership", "Change Management", "Emotional Intelligence", "Conflict Resolution"]', 3.0, "Fall", False),
    ("Babson", None, "ENT7500", "Venture Growth Strategies", "Scaling startups, growth metrics, expansion planning", '["Scaling Operations", "Growth Hacking", "Unit Economics", "Go-to-Market Strategy"]', 3.0, "Spring", True),
    ("Babson", None, "FIN7500", "Venture Finance", "Startup financing, term sheets, cap tables, VC dynamics", '["Venture Financing", "Cap Table Management", "Fundraising Strategy", "Venture Capital"]', 3.0, "Spring", True),
    ("Babson", None, "QTM6100", "Data Analytics for Managers", "Statistics, data analysis, business intelligence", '["Statistical Analysis", "Data Visualization", "Python Programming", "SQL & Database Management"]', 3.0, "Fall", False),
    ("Babson", None, "ENT7200", "New Venture Creation", "From idea to launch: opportunity assessment, business planning", '["Business Model Canvas", "Customer Discovery", "Market Sizing (TAM/SAM/SOM)", "Minimum Viable Product (MVP) Design"]', 3.0, "Spring", True),
    ("Babson", None, "STR8300", "Competitive Strategy", "Industry analysis, competitive positioning, strategic decision-making", '["Corporate Strategy", "Competitive Analysis", "Strategic Thinking"]', 3.0, "Spring", True),
    ("Babson", None, "MKT8400", "Digital Marketing Strategy", "SEO, social media, content marketing, marketing automation", '["SEO / SEM", "Social Media Analytics", "Digital Marketing Analytics", "Growth Marketing"]', 3.0, "Spring", True),
    ("Babson", None, "FIN8500", "Private Equity & Venture Capital", "PE/VC fund structure, deal evaluation, portfolio management", '["Private Equity", "Venture Capital", "Valuation Methods", "Due Diligence (Startup)"]', 3.0, "Fall", True),
    ("Babson", None, "TEC8100", "AI for Business Leaders", "AI strategy, implementation, governance, use cases", '["AI Strategy & Governance", "Machine Learning Fundamentals", "Digital Transformation"]', 3.0, "Fall", True),
    ("Babson", None, "ENT8600", "Social Innovation & Impact", "Social entrepreneurship, impact measurement, B-Corps", '["Social Enterprise Models", "Impact Measurement", "Nonprofit Management"]', 3.0, "Spring", True),

    # HBS representative courses
    ("HBS", None, "FIN1", "Finance I", "Foundational corporate finance, NPV, cost of capital", '["Financial Modeling", "Valuation Methods", "Revenue Forecasting"]', 3.0, "Fall", False),
    ("HBS", None, "TEM", "The Entrepreneurial Manager", "Entrepreneurship and innovation management", '["Business Model Canvas", "Lean Startup Methodology", "Entrepreneurship", "Venture Financing"]', 3.0, "Spring", False),
    ("HBS", None, "LCA", "Leadership and Corporate Accountability", "Ethics, governance, corporate responsibility", '["Ethics & Integrity", "Stakeholder Management", "Corporate Strategy"]', 3.0, "Fall", False),

    # MIT Sloan
    ("MIT Sloan", None, "15.390", "New Enterprises", "MIT's flagship entrepreneurship course", '["Business Model Canvas", "Customer Discovery", "Minimum Viable Product (MVP) Design", "Pitching & Storytelling"]', 3.0, "Fall/Spring", True),
    ("MIT Sloan", None, "15.003", "Analytics Lab", "Hands-on analytics with real company projects", '["Machine Learning Fundamentals", "Python Programming", "Data Visualization", "Statistical Analysis"]', 3.0, "Spring", True),
    ("MIT Sloan", None, "15.401", "Finance Theory I", "Asset pricing, capital markets, portfolio theory", '["Financial Modeling", "Quantitative Risk Analysis", "Derivative Pricing"]', 3.0, "Fall", False),

    # BU Questrom
    ("BU Questrom", None, "QST MG920", "Health Sector Management", "Healthcare industry management and strategy", '["Healthcare Management", "Healthcare Economics", "Strategic Thinking"]', 3.0, "Fall", True),
    ("BU Questrom", None, "QST BA830", "Business Analytics", "Data-driven decision making", '["Statistical Analysis", "Python Programming", "Data Visualization", "Machine Learning Fundamentals"]', 3.0, "Fall", False),

    # Northeastern
    ("Northeastern", None, "MKTG6225", "Digital Marketing Analytics", "Web analytics, attribution, experimentation", '["Digital Marketing Analytics", "A/B Testing & Experimentation", "Social Media Analytics"]', 3.0, "Fall", True),
    ("Northeastern", None, "ENTR6200", "Entrepreneurial Innovation", "Innovation frameworks and startup methods", '["Lean Startup Methodology", "Design Thinking", "Rapid Prototyping"]', 3.0, "Spring", True),

    # Bentley
    ("Bentley", None, "FI621", "Investment Analysis", "Security analysis, portfolio management", '["Valuation Methods", "Financial Modeling", "Quantitative Risk Analysis"]', 3.0, "Fall", True),
    ("Bentley", None, "MK670", "Marketing Analytics", "Advanced marketing data analysis", '["Digital Marketing Analytics", "Statistical Analysis", "A/B Testing & Experimentation", "Product Analytics"]', 3.0, "Spring", True),
]

# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
PROJECTS_DATA = [
    ("Startup Weekend: Build & Launch MVP", "48-hour sprint to go from idea to functioning MVP with customer validation", "startup", '["Business Model Canvas", "Minimum Viable Product (MVP) Design", "Customer Discovery", "Pitching & Storytelling", "Rapid Prototyping"]', '["Technology", "Entrepreneurship", "Consumer Goods"]', "intermediate", 48),
    ("Consulting Capstone: Fortune 500 Strategy", "Team-based consulting engagement solving a real strategic challenge for a major corporation", "capstone", '["Management Consulting Frameworks", "Corporate Strategy", "Communication (Verbal)", "Team Leadership", "Data Visualization"]', '["Consulting", "Technology", "Financial Services"]', "advanced", 200),
    ("Venture Capital Investment Memo", "Analyze a real startup and produce a full investment recommendation memo", "independent", '["Venture Capital", "Valuation Methods", "Financial Modeling", "Market Sizing (TAM/SAM/SOM)", "Due Diligence (Startup)"]', '["Financial Services", "Technology", "Healthcare"]', "advanced", 80),
    ("Data Analytics for Social Impact", "Use data science to solve a problem for a local nonprofit", "consulting", '["Python Programming", "Data Visualization", "Statistical Analysis", "Impact Measurement", "Stakeholder Management"]', '["Nonprofit", "Healthcare", "Education Technology"]', "intermediate", 120),
    ("Digital Marketing Campaign", "Design and execute a full digital marketing campaign for a real business", "independent", '["Digital Marketing Analytics", "SEO / SEM", "Social Media Analytics", "A/B Testing & Experimentation", "Growth Marketing"]', '["Consumer Goods", "Technology", "Retail & E-commerce"]', "beginner", 60),
    ("Financial Modeling Competition", "Build a comprehensive 3-statement financial model for a public company", "competition", '["Financial Modeling", "Valuation Methods", "Excel / Google Sheets (Advanced)", "Revenue Forecasting", "Accounting (GAAP)"]', '["Financial Services", "Investment Banking", "Private Equity"]', "advanced", 40),
    ("Healthcare Innovation Lab", "Develop a healthtech solution addressing a real clinical workflow problem", "capstone", '["Healthcare Management", "Design Thinking", "Minimum Viable Product (MVP) Design", "Customer Discovery", "HealthTech"]', '["Healthcare", "Technology", "Entrepreneurship"]', "advanced", 160),
    ("Supply Chain Optimization Project", "Analyze and optimize supply chain for a manufacturing company", "consulting", '["Supply Chain Analytics", "Operations Research", "Data Visualization", "Python Programming", "Operations Strategy"]', '["Manufacturing & Operations", "Consumer Goods", "Retail & E-commerce"]', "intermediate", 100),
    ("Product Management Simulation", "End-to-end product lifecycle management with cross-functional teams", "capstone", '["Technology Product Management", "Agile / Scrum Methodology", "Product Analytics", "UX/UI Design Principles", "Cross-functional Collaboration"]', '["Technology", "Consumer Goods", "Financial Services"]', "intermediate", 80),
    ("International Market Entry Strategy", "Develop a market entry plan for a company expanding to emerging markets", "research", '["Emerging Markets Strategy", "International Trade", "Market Research Methods", "Global Perspective", "Competitive Analysis"]', '["Consumer Goods", "Technology", "Financial Services"]', "advanced", 100),
    ("AI Business Application Prototype", "Build an AI-powered tool that solves a real business problem", "independent", '["Machine Learning Fundamentals", "Python Programming", "AI Strategy & Governance", "Product Analytics", "Rapid Prototyping"]', '["Technology", "Financial Services", "Healthcare"]', "advanced", 120),
    ("Real Estate Development Pro Forma", "Create a full financial analysis for a mixed-use development project", "independent", '["Real Estate Financial Analysis", "Financial Modeling", "Revenue Forecasting", "Excel / Google Sheets (Advanced)"]', '["Real Estate Development", "Financial Services"]', "intermediate", 60),
    ("Business Plan Competition Entry", "Write and present a complete business plan for a new venture", "competition", '["Business Model Canvas", "Startup Financial Projections", "Market Sizing (TAM/SAM/SOM)", "Pitching & Storytelling", "Go-to-Market Strategy"]', '["Entrepreneurship", "Technology", "Consumer Goods"]', "intermediate", 100),
    ("ESG & Sustainability Audit", "Conduct an ESG audit for a real company and develop improvement recommendations", "consulting", '["Energy & Sustainability", "Social Impact Investing", "Impact Measurement", "Regulatory Compliance"]', '["Energy & Sustainability", "Financial Services", "Consumer Goods"]', "intermediate", 80),
    ("SaaS Metrics Dashboard", "Build an interactive dashboard tracking key SaaS business metrics", "independent", '["SaaS Business Models", "Product Analytics", "Data Visualization", "Tableau / Power BI", "Unit Economics"]', '["Technology", "Financial Services"]', "intermediate", 40),
]

# ---------------------------------------------------------------------------
# Job-Skills Mappings
# ---------------------------------------------------------------------------
JOB_SKILLS_DATA = [
    # Product Manager
    ("Product Manager", "Technology", "Technology Product Management", 5, "essential"),
    ("Product Manager", "Technology", "Agile / Scrum Methodology", 4, "essential"),
    ("Product Manager", "Technology", "Data Visualization", 4, "common"),
    ("Product Manager", "Technology", "SQL & Database Management", 3, "common"),
    ("Product Manager", "Technology", "UX/UI Design Principles", 4, "common"),
    ("Product Manager", "Technology", "Communication (Verbal)", 5, "essential"),
    ("Product Manager", "Technology", "Strategic Thinking", 4, "essential"),
    ("Product Manager", "Technology", "Cross-functional Collaboration", 5, "essential"),
    ("Product Manager", "Technology", "A/B Testing & Experimentation", 3, "common"),
    ("Product Manager", "Technology", "Product Analytics", 4, "essential"),

    # Management Consultant
    ("Management Consultant", "Consulting", "Management Consulting Frameworks", 5, "essential"),
    ("Management Consultant", "Consulting", "Communication (Verbal)", 5, "essential"),
    ("Management Consultant", "Consulting", "Communication (Written)", 5, "essential"),
    ("Management Consultant", "Consulting", "Excel / Google Sheets (Advanced)", 4, "essential"),
    ("Management Consultant", "Consulting", "Data Visualization", 4, "common"),
    ("Management Consultant", "Consulting", "Strategic Thinking", 5, "essential"),
    ("Management Consultant", "Consulting", "Problem Solving", 5, "essential"),
    ("Management Consultant", "Consulting", "Team Leadership", 4, "common"),
    ("Management Consultant", "Consulting", "Presentation Design", 4, "common"),
    ("Management Consultant", "Consulting", "Stakeholder Management", 4, "common"),

    # Investment Banking Associate
    ("Investment Banking Associate", "Financial Services", "Financial Modeling", 5, "essential"),
    ("Investment Banking Associate", "Financial Services", "Valuation Methods", 5, "essential"),
    ("Investment Banking Associate", "Financial Services", "Mergers & Acquisitions Analysis", 5, "essential"),
    ("Investment Banking Associate", "Financial Services", "Excel / Google Sheets (Advanced)", 5, "essential"),
    ("Investment Banking Associate", "Financial Services", "Accounting (GAAP)", 4, "common"),
    ("Investment Banking Associate", "Financial Services", "Presentation Design", 4, "common"),
    ("Investment Banking Associate", "Financial Services", "Communication (Written)", 4, "essential"),
    ("Investment Banking Associate", "Financial Services", "Time Management", 5, "essential"),

    # Startup Founder
    ("Startup Founder", "Entrepreneurship", "Business Model Canvas", 5, "essential"),
    ("Startup Founder", "Entrepreneurship", "Lean Startup Methodology", 5, "essential"),
    ("Startup Founder", "Entrepreneurship", "Customer Discovery", 5, "essential"),
    ("Startup Founder", "Entrepreneurship", "Pitching & Storytelling", 5, "essential"),
    ("Startup Founder", "Entrepreneurship", "Fundraising Strategy", 4, "essential"),
    ("Startup Founder", "Entrepreneurship", "Unit Economics", 4, "essential"),
    ("Startup Founder", "Entrepreneurship", "Go-to-Market Strategy", 4, "essential"),
    ("Startup Founder", "Entrepreneurship", "Team Leadership", 5, "essential"),
    ("Startup Founder", "Entrepreneurship", "Resilience", 5, "essential"),
    ("Startup Founder", "Entrepreneurship", "Product-Market Fit", 5, "essential"),
    ("Startup Founder", "Entrepreneurship", "Minimum Viable Product (MVP) Design", 4, "essential"),
    ("Startup Founder", "Entrepreneurship", "Startup Financial Projections", 4, "common"),

    # Data Scientist
    ("Data Scientist", "Technology", "Python Programming", 5, "essential"),
    ("Data Scientist", "Technology", "SQL & Database Management", 5, "essential"),
    ("Data Scientist", "Technology", "Machine Learning Fundamentals", 5, "essential"),
    ("Data Scientist", "Technology", "Statistical Analysis", 5, "essential"),
    ("Data Scientist", "Technology", "Data Visualization", 4, "essential"),
    ("Data Scientist", "Technology", "Communication (Verbal)", 3, "common"),
    ("Data Scientist", "Technology", "Natural Language Processing", 3, "nice-to-have"),
    ("Data Scientist", "Technology", "A/B Testing & Experimentation", 4, "common"),

    # Marketing Manager
    ("Marketing Manager", "Consumer Goods", "Marketing Strategy", 5, "essential"),
    ("Marketing Manager", "Consumer Goods", "Digital Marketing Analytics", 4, "essential"),
    ("Marketing Manager", "Consumer Goods", "Market Research Methods", 4, "common"),
    ("Marketing Manager", "Consumer Goods", "Communication (Written)", 5, "essential"),
    ("Marketing Manager", "Consumer Goods", "SEO / SEM", 3, "common"),
    ("Marketing Manager", "Consumer Goods", "Social Media Analytics", 4, "common"),
    ("Marketing Manager", "Consumer Goods", "Growth Marketing", 4, "essential"),
    ("Marketing Manager", "Consumer Goods", "Pricing Strategy Models", 3, "common"),
    ("Marketing Manager", "Consumer Goods", "Creative & Innovation", 4, "common"),
    ("Marketing Manager", "Consumer Goods", "Stakeholder Management", 3, "common"),

    # VC Associate
    ("Venture Capital Associate", "Financial Services", "Venture Capital", 5, "essential"),
    ("Venture Capital Associate", "Financial Services", "Financial Modeling", 4, "essential"),
    ("Venture Capital Associate", "Financial Services", "Market Sizing (TAM/SAM/SOM)", 5, "essential"),
    ("Venture Capital Associate", "Financial Services", "Due Diligence (Startup)", 5, "essential"),
    ("Venture Capital Associate", "Financial Services", "Valuation Methods", 4, "common"),
    ("Venture Capital Associate", "Financial Services", "Networking", 4, "essential"),
    ("Venture Capital Associate", "Financial Services", "Unit Economics", 4, "essential"),
    ("Venture Capital Associate", "Financial Services", "Communication (Written)", 4, "essential"),

    # PE Associate
    ("Private Equity Associate", "Financial Services", "Private Equity", 5, "essential"),
    ("Private Equity Associate", "Financial Services", "Financial Modeling", 5, "essential"),
    ("Private Equity Associate", "Financial Services", "Valuation Methods", 5, "essential"),
    ("Private Equity Associate", "Financial Services", "Mergers & Acquisitions Analysis", 5, "essential"),
    ("Private Equity Associate", "Financial Services", "Accounting (GAAP)", 4, "common"),
    ("Private Equity Associate", "Financial Services", "Excel / Google Sheets (Advanced)", 5, "essential"),
    ("Private Equity Associate", "Financial Services", "Analytical Reasoning", 5, "essential"),

    # Healthcare Manager
    ("Healthcare Manager", "Healthcare", "Healthcare Management", 5, "essential"),
    ("Healthcare Manager", "Healthcare", "Healthcare Economics", 4, "essential"),
    ("Healthcare Manager", "Healthcare", "Operations Strategy", 4, "common"),
    ("Healthcare Manager", "Healthcare", "Regulatory Compliance", 4, "essential"),
    ("Healthcare Manager", "Healthcare", "Stakeholder Management", 4, "essential"),
    ("Healthcare Manager", "Healthcare", "Change Management", 4, "common"),
    ("Healthcare Manager", "Healthcare", "Data Visualization", 3, "common"),

    # Operations Manager
    ("Operations Manager", "Manufacturing & Operations", "Operations Strategy", 5, "essential"),
    ("Operations Manager", "Manufacturing & Operations", "Supply Chain Management", 5, "essential"),
    ("Operations Manager", "Manufacturing & Operations", "Quality Management (Six Sigma)", 4, "essential"),
    ("Operations Manager", "Manufacturing & Operations", "Project Management Tools", 4, "common"),
    ("Operations Manager", "Manufacturing & Operations", "Supply Chain Analytics", 4, "common"),
    ("Operations Manager", "Manufacturing & Operations", "Team Leadership", 4, "essential"),
    ("Operations Manager", "Manufacturing & Operations", "Problem Solving", 5, "essential"),
]


def seed():
    init_db()

    with get_connection() as conn:
        # Schools
        school_id_map = {}
        for s in SCHOOLS:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO schools (name, short_name, location, school_type, ranking_us_news, ranking_entrepreneurship, website_url, career_report_url) VALUES (?,?,?,?,?,?,?,?)",
                s,
            )
            if cursor.lastrowid:
                school_id_map[s[1]] = cursor.lastrowid
            else:
                row = conn.execute("SELECT id FROM schools WHERE short_name = ?", (s[1],)).fetchone()
                school_id_map[s[1]] = row["id"]

        # Programs
        for short_name, progs in PROGRAMS.items():
            sid = school_id_map[short_name]
            for p in progs:
                conn.execute(
                    "INSERT OR IGNORE INTO programs (school_id, name, degree_type, concentration, duration_months, format) VALUES (?,?,?,?,?,?)",
                    (sid, *p),
                )

        # Skills
        skill_id_map = {}
        for s in SKILLS:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO skills (name, category, subcategory, description) VALUES (?,?,?,?)",
                s,
            )
            if cursor.lastrowid:
                skill_id_map[s[0]] = cursor.lastrowid
            else:
                row = conn.execute("SELECT id FROM skills WHERE name = ?", (s[0],)).fetchone()
                skill_id_map[s[0]] = row["id"]

        # Skill synonyms
        for canonical, syns in SKILL_SYNONYMS.items():
            if canonical in skill_id_map:
                for syn in syns:
                    conn.execute(
                        "INSERT OR IGNORE INTO skill_synonyms (skill_id, synonym, source) VALUES (?,?,?)",
                        (skill_id_map[canonical], syn, "seed"),
                    )

        # Transferable skills
        for t in TRANSFERABLE_MAPPINGS:
            skill_name, from_ctx, to_ctx, score, rationale = t
            if skill_name in skill_id_map:
                conn.execute(
                    "INSERT OR IGNORE INTO transferable_skills (skill_id, from_context, to_context, relevance_score, mapping_rationale) VALUES (?,?,?,?,?)",
                    (skill_id_map[skill_name], from_ctx, to_ctx, score, rationale),
                )

        # Job outcomes
        for o in JOB_OUTCOMES:
            school_short = o[0]
            sid = school_id_map[school_short]
            conn.execute(
                "INSERT INTO job_outcomes (school_id, report_year, industry, job_function, company, job_title, median_salary, mean_salary, signing_bonus, employment_rate_at_grad, employment_rate_3mo, employment_rate_6mo, pct_of_class, source_url) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (sid, *o[1:], None),
            )

        # Courses
        for c in COURSES_DATA:
            school_short = c[0]
            sid = school_id_map[school_short]
            conn.execute(
                "INSERT OR IGNORE INTO courses (school_id, program_id, course_code, name, description, skills_taught, credits, semester, is_elective) VALUES (?,?,?,?,?,?,?,?,?)",
                (sid, None, *c[2:]),
            )

        # Projects
        for p in PROJECTS_DATA:
            conn.execute(
                "INSERT OR IGNORE INTO projects (title, description, project_type, skills_developed, industry_relevance, difficulty, estimated_hours) VALUES (?,?,?,?,?,?,?)",
                p,
            )

        # Job-Skills mappings
        for js in JOB_SKILLS_DATA:
            job_title, industry, skill_name, importance, frequency = js
            if skill_name in skill_id_map:
                conn.execute(
                    "INSERT OR IGNORE INTO job_skills (job_title, industry, skill_id, importance_score, frequency, source) VALUES (?,?,?,?,?,?)",
                    (job_title, industry, skill_id_map[skill_name], importance, frequency, "seed"),
                )

    print(f"Seeded database at {Path(str(conn)).name if hasattr(conn, 'name') else 'career_platform.db'}")
    print(f"  Schools: {len(SCHOOLS)}")
    print(f"  Skills: {len(SKILLS)}")
    print(f"  Job outcomes: {len(JOB_OUTCOMES)}")
    print(f"  Courses: {len(COURSES_DATA)}")
    print(f"  Projects: {len(PROJECTS_DATA)}")
    print(f"  Job-skill mappings: {len(JOB_SKILLS_DATA)}")


if __name__ == "__main__":
    seed()
