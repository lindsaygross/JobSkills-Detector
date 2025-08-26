def detect_skills(text: str):
    SKILLS = ["python", "sql", "excel", "pandas", "numpy", "scikit-learn", "tableau", "git", "aws"]
    found = []
    if text:
        t = text.lower()
        for skill in SKILLS:
            if skill in t:
                found.append(skill)
    return sorted(set(found))


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """Extract text from uploaded PDF file bytes."""
    from pypdf import PdfReader
    import io
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text
