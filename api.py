def detect_skills(text: str):
    SKILLS = ["python", "sql", "excel", "pandas", "numpy", "scikit-learn", "tableau", "git", "aws"]
    found = []
    if text:
        t = text.lower()
        for skill in SKILLS:
            if skill in t:
                found.append(skill)
    return sorted(set(found))
