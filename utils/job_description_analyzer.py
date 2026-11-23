
import re

# Technical and professional skills with alternative names
SKILLS_DICT = {
    "Python": ["python", "python3"],
    "Java": ["java"],
    "C": ["c programming", "c language", "programming in c"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "c sharp"],
    "SQL": ["sql", "structured query language"],
    "HTML": ["html"],
    "CSS": ["css"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript"],
    "React": ["react", "reactjs", "react.js"],
    "Angular": ["angular"],
    "Node.js": ["node.js", "nodejs"],
    "Machine Learning": ["machine learning", "machine-learning"],
    "Deep Learning": ["deep learning", "deep-learning"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Data Science": ["data science"],
    "Artificial Intelligence": ["artificial intelligence"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "MATLAB": ["matlab"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Linux": ["linux"],
    "Flask": ["flask"],
    "Django": ["django"],
    "FastAPI": ["fastapi"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql"],
    "MongoDB": ["mongodb"],
    "AWS": ["amazon web services", "aws"],
    "Azure": ["microsoft azure", "azure"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes"],
    "REST API": ["rest api", "rest apis", "restful api", "restful apis"],
    "Data Structures": ["data structures"],
    "Algorithms": ["algorithms", "algorithm design"],
    "Object-Oriented Programming": [
        "object oriented programming",
        "object-oriented programming",
        "oop"
    ],
    "Database Management": ["database management"],
    "Software Development": ["software development"],
    "Problem Solving": ["problem solving", "problem-solving"],
    "Communication": ["communication skills", "communication"],
    "Teamwork": ["teamwork", "team work", "team collaboration"],
    "Leadership": ["leadership"],
    "Time Management": ["time management"],
    "Critical Thinking": ["critical thinking"]
}


def normalize_skill(skill):
    """Convert a skill or synonym into its canonical name."""

    if not isinstance(skill, str):
        return None

    skill = skill.strip().lower()

    for canonical, synonyms in SKILLS_DICT.items():
        if skill == canonical.lower():
            return canonical

        if skill in [s.lower() for s in synonyms]:
            return canonical

    return None


def extract_skills(text):
    """Extract unique skills from text."""

    if not isinstance(text, str) or not text.strip():
        return []

    found_skills = []

    for canonical, synonyms in SKILLS_DICT.items():

        terms = [canonical] + synonyms

        for term in terms:

            # Avoid detecting the single letter C without context
            if canonical == "C" and term.lower() == "c":
                continue

            pattern = (
                r"(?<![a-zA-Z0-9+#])"
                + re.escape(term)
                + r"(?![a-zA-Z0-9+#])"
            )

            if re.search(pattern, text, re.IGNORECASE):
                found_skills.append(canonical)
                break

        # Detect C only with programming context
        if canonical == "C":
            c_patterns = [
                r"\bC\s+programming\b",
                r"\bC\s+language\b",
                r"\bprogramming\s+in\s+C\b"
            ]

            if any(
                re.search(p, text, re.IGNORECASE)
                for p in c_patterns
            ):
                found_skills.append("C")

    return list(dict.fromkeys(found_skills))


def compare_skills(resume_skills, job_required_skills):
    """Compare resume skills against required job skills."""

    resume_set = {
        normalize_skill(skill)
        for skill in resume_skills
        if normalize_skill(skill)
    }

    required_set = {
        normalize_skill(skill)
        for skill in job_required_skills
        if normalize_skill(skill)
    }

    matching = [
        skill for skill in job_required_skills
        if normalize_skill(skill) in resume_set
        and normalize_skill(skill) in required_set
    ]

    missing = [
        skill for skill in job_required_skills
        if normalize_skill(skill) in required_set
        and normalize_skill(skill) not in resume_set
    ]

    matching = list(dict.fromkeys(
        normalize_skill(skill) for skill in matching
    ))

    missing = list(dict.fromkeys(
        normalize_skill(skill) for skill in missing
    ))

    return matching, missing


def calculate_match_percentage(resume_skills, job_required_skills):
    """Calculate the percentage of required skills found in resume."""

    matching, missing = compare_skills(
        resume_skills,
        job_required_skills
    )

    total_required = len({
        normalize_skill(skill)
        for skill in job_required_skills
        if normalize_skill(skill)
    })

    if total_required == 0:
        return 0.0

    return round(len(matching) / total_required * 100, 2)


def extract_keywords(text):
    """Extract important job description keywords."""

    if not isinstance(text, str) or not text.strip():
        return []

    keywords = extract_skills(text)

    phrases = [
        "web development",
        "software development",
        "data science",
        "artificial intelligence",
        "natural language processing",
        "cloud computing",
        "database management",
        "software engineering",
        "project management",
        "problem solving",
        "team collaboration",
        "debugging",
        "software testing",
        "version control"
    ]

    for phrase in phrases:
        pattern = (
            r"(?<!\w)"
            + re.escape(phrase)
            + r"(?!\w)"
        )

        if re.search(pattern, text, re.IGNORECASE):
            keywords.append(phrase.title())

    return list(dict.fromkeys(keywords))


def generate_suggestions(missing_skills):
    """Generate suggestions based on missing skills."""

    if not missing_skills:
        return [
            "Your resume covers all the identified required skills.",
            "Continue improving your project descriptions and achievements."
        ]

    suggestions = []

    for skill in missing_skills:
        suggestions.append(
            f"If you have experience with {skill}, "
            f"include it in your technical skills or relevant projects. "
            f"Otherwise, consider learning it through practical projects."
        )

    return suggestions


# Independent testing
if __name__ == "__main__":

    resume_text = """
    I know Python, Java, SQL, React and Machine Learning.
    I have worked on Data Analysis projects.
    """

    job_text = """
    Required skills: Python, Java, SQL, React,
    Machine Learning, Deep Learning and TensorFlow.
    """

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    matching, missing = compare_skills(
        resume_skills,
        job_skills
    )

    score = calculate_match_percentage(
        resume_skills,
        job_skills
    )

    print("Resume Skills:", resume_skills)
    print("Required Skills:", job_skills)
    print("Matching Skills:", matching)
    print("Missing Skills:", missing)
    print("Match Percentage:", score, "%")
    print("Keywords:", extract_keywords(job_text))
    print("Suggestions:", generate_suggestions(missing))
