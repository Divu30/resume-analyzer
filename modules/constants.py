"""
constants.py
------------
Static data used across the Intelligent Resume Analyzer:
- STOPWORDS: common English words ignored during text analysis
- SKILL_KEYWORDS: master list of known skill keywords (tech + soft skills)
- EDUCATION_KEYWORDS: degree/education keywords
No external packages are used anywhere in this project.
"""

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "so", "of", "in",
    "on", "at", "for", "to", "from", "by", "with", "about", "as", "into",
    "like", "through", "after", "over", "between", "out", "against",
    "during", "without", "before", "under", "around", "among", "is",
    "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "shall", "should", "can",
    "could", "may", "might", "must", "this", "that", "these", "those",
    "i", "you", "he", "she", "it", "we", "they", "them", "his", "her",
    "its", "our", "their", "my", "your", "me", "him", "us", "not", "no",
    "yes", "up", "down", "off", "again", "further", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each",
    "few", "more", "most", "other", "some", "such", "only", "own",
    "same", "than", "too", "very", "just", "also", "etc", "e.g", "i.e",
    "job", "role", "position", "candidate", "candidates", "company",
    "team", "work", "working", "years", "year", "experience", "required",
    "requirements", "responsibilities", "including", "including but",
    "preferred", "plus", "strong", "excellent", "good", "ability",
    "skills", "skill", "knowledge", "familiarity", "understanding",
}

# Master skill keyword list (lowercase). Extend freely.
SKILL_KEYWORDS = {
    # Programming Languages
    "python", "java", "c", "c++", "c#", "javascript", "typescript", "go",
    "golang", "ruby", "php", "swift", "kotlin", "r", "matlab", "scala",
    "perl", "rust", "dart", "sql", "html", "css", "bash", "shell",

    # Web / Frameworks
    "react", "reactjs", "angular", "vue", "vuejs", "node", "nodejs",
    "express", "django", "flask", "fastapi", "spring", "springboot",
    "laravel", "asp.net", "jquery", "bootstrap", "tailwind", "next.js",
    "nextjs", "redux", "graphql", "rest", "restapi", "soap",

    # Data / AI / ML
    "machine learning", "deep learning", "artificial intelligence",
    "data science", "data analysis", "data analytics", "nlp",
    "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
    "sklearn", "pandas", "numpy", "matplotlib", "seaborn", "opencv",
    "power bi", "tableau", "excel", "statistics", "big data", "hadoop",
    "spark", "pyspark", "etl", "data visualization", "data mining",
    "data warehousing", "data modeling",

    # Databases
    "mysql", "postgresql", "postgres", "mongodb", "sqlite", "oracle",
    "redis", "cassandra", "firebase", "dynamodb", "nosql", "database",
    "elasticsearch",

    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "jenkins", "ci/cd", "cicd", "terraform", "ansible", "linux", "unix",
    "git", "github", "gitlab", "bitbucket", "devops", "microservices",
    "nginx", "apache",

    # Mobile
    "android", "ios", "flutter", "react native", "xamarin",

    # Testing
    "selenium", "junit", "pytest", "testng", "manual testing",
    "automation testing", "unit testing", "test cases", "qa",

    # Tools
    "jira", "confluence", "trello", "figma", "photoshop", "illustrator",
    "postman", "vs code", "visual studio", "eclipse", "intellij",

    # Methodologies
    "agile", "scrum", "kanban", "waterfall", "sdlc", "devsecops",

    # Soft Skills
    "communication", "leadership", "teamwork", "problem solving",
    "critical thinking", "time management", "adaptability", "creativity",
    "collaboration", "presentation", "negotiation", "decision making",
    "project management", "analytical", "mentoring", "multitasking",
    "attention to detail", "organizational", "interpersonal",

    # Business / Domain
    "accounting", "finance", "marketing", "sales", "seo", "sem",
    "content writing", "digital marketing", "operations", "logistics",
    "supply chain", "hr", "recruitment", "customer service",
    "business analysis", "product management", "crm", "erp", "sap",

    # Misc Tech
    "api", "json", "xml", "oop", "algorithms", "data structures",
    "system design", "networking", "cybersecurity", "blockchain",
    "cryptography", "iot", "embedded systems", "robotics",
}

EDUCATION_KEYWORDS = {
    "phd": 4, "ph.d": 4, "doctorate": 4,
    "master": 3, "masters": 3, "m.tech": 3, "mtech": 3, "mba": 3,
    "m.sc": 3, "msc": 3, "m.e": 3, "me": 3, "postgraduate": 3,
    "bachelor": 2, "bachelors": 2, "b.tech": 2, "btech": 2,
    "b.sc": 2, "bsc": 2, "b.e": 2, "be": 2, "undergraduate": 2,
    "graduate": 2,
    "diploma": 1, "associate": 1, "high school": 1, "hsc": 1,
}
