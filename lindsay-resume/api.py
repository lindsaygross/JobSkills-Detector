# api.py
import re
import io
import math
import html
import json
from typing import Dict, List, Tuple
import requests

# -------- Resume text extraction --------
from pypdf import PdfReader

def extract_text_from_file(file_name: str, file_bytes: bytes) -> str:
    name = (file_name or "").lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = [p.extract_text() or "" for p in reader.pages]
        return "\n".join(pages)
    elif name.endswith(".txt"):
        try:
            return file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            return file_bytes.decode("latin-1", errors="ignore")
    else:
        # Fallback: try utf-8 as plain text
        return file_bytes.decode("utf-8", errors="ignore")

# -------- Skill catalog (edit to taste) --------
SKILL_ALIASES = {
    # Core data & Python
    "python": ["python", "py"],
    "pandas": ["pandas"],
    "numpy": ["numpy", "np"],
    "sql": ["sql", "postgres", "postgresql", "mysql", "sqlite", "snowflake", "bigquery", "mssql", "sql server"],
    "excel": ["excel", "microsoft excel", "pivot table", "vlookup"],
    "git": ["git", "github", "gitlab"],

    # ML / AI
    "scikit-learn": ["scikit-learn", "sklearn"],
    "tensorflow": ["tensorflow", "tf"],
    "pytorch": ["pytorch", "torch"],
    "xgboost": ["xgboost"],
    "lightgbm": ["lightgbm", "lgbm"],
    "nlp": ["nlp", "natural language processing"],
    "computer vision": ["computer vision", "cv"],

    # GenAI / RAG
    "openai api": ["openai", "chatgpt api", "gpt-4", "gpt4", "gpt-3.5"],
    "hugging face": ["huggingface", "hugging face", "transformers"],
    "vector db": ["faiss", "pinecone", "weaviate", "milvus", "chromadb"],

    # Apps / Web
    "streamlit": ["streamlit"],
    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "rest api": ["rest", "rest api", "http api"],

    # Cloud / Infra
    "aws": ["aws", "amazon web services", "s3", "lambda", "ec2", "athena", "redshift"],
    "gcp": ["gcp", "google cloud", "bigquery", "vertex ai"],
    "azure": ["azure", "azure ml"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],

    # Data platforms
    "spark": ["spark", "pyspark"],
    "airflow": ["airflow", "apache airflow"],
    "dbt": ["dbt"],
}

CANONICAL_SKILLS: List[str] = list(SKILL_ALIASES.keys())

# -------- Simple keyword detector (hybrid boost) --------
def detect_skills_keyword(text: str) -> Dict[str, int]:
    if not text:
        return {}
    t = text.lower()
    counts: Dict[str, int] = {}
    for canon, aliases in SKILL_ALIASES.items():
        hit = 0
        for alias in aliases:
            # allow space/_/- between words
            patt = re.escape(alias).replace(r"\ ", r"[ _-]+").replace(r"\-", r"[ _-]+")
            found = re.findall(rf"\b{patt}\b", t, flags=re.IGNORECASE)
            hit += len(found)
        if hit:
            counts[canon] = hit
    return counts

# -------- Local embeddings (MiniLM) --------
# Lazy-load so import is fast on CLI
_MODEL = None
_SKILL_EMB = None


def _get_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        # Force CPU to avoid MPS/Metal meta-tensor issues on macOS
        _MODEL = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            device="cpu",
        )
    return _MODEL


def _embed(texts: List[str]):
    model = _get_model()
    # returns list of numpy arrays
    embs = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    return embs

def _get_skill_embeddings():
    global _SKILL_EMB
    if _SKILL_EMB is None:
        phrases = CANONICAL_SKILLS  # one embedding per canonical skill name
        _SKILL_EMB = _embed(phrases)
    return _SKILL_EMB

def semantic_skill_scores(text: str) -> Dict[str, float]:
    """
    Cosine similarity between the document embedding and each canonical skill phrase.
    Returns {skill: score in [0,1]}.
    """
    if not text or not text.strip():
        return {}
    doc_emb = _embed([text])[0]  # (d,)
    skill_embs = _get_skill_embeddings()  # (k,d)
    # cosine similarity since embs are normalized -> dot product
    import numpy as np
    sims = np.dot(skill_embs, doc_emb)  # (k,)
    # rescale from [-1,1] to [0,1] for easier reading
    sims01 = (sims + 1) / 2.0
    return {CANONICAL_SKILLS[i]: float(sims01[i]) for i in range(len(CANONICAL_SKILLS))}

def hybrid_skill_scores(text: str, keyword_boost: float = 0.25) -> Dict[str, float]:
    """
    Combines semantic similarity with a small keyword boost if found.
    """
    sims = semantic_skill_scores(text)
    kw = detect_skills_keyword(text)
    out = {}
    for s, val in sims.items():
        boost = keyword_boost if kw.get(s, 0) > 0 else 0.0
        out[s] = max(0.0, min(1.0, val + boost))
    return out

# -------- Free jobs API (Remotive) --------
REMOTIVE_URL = "https://remotive.com/api/remote-jobs"

def _strip_html(s: str) -> str:
    s = html.unescape(s or "")
    return re.sub(r"<[^>]+>", " ", s)

def fetch_jobs_remotive(query: str, limit: int = 10) -> List[Dict]:
    """
    Returns a list of jobs with keys: title, company, description (plain text).
    """
    params = {"search": query or ""}
    resp = requests.get(REMOTIVE_URL, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    jobs = data.get("jobs", [])[:max(1, limit)]
    out = []
    for j in jobs:
        out.append({
            "title": j.get("title", ""),
            "company": j.get("company_name", ""),
            "url": j.get("url", ""),  # APPLY / job detail link
            "location": j.get("candidate_required_location", ""),
            "date": j.get("publication_date", "")[:10],
            "description": _strip_html(j.get("description", "")),
        })
    return out

def aggregate_job_skill_scores(jobs: List[Dict]) -> Dict[str, float]:
    """
    Average hybrid scores across job descriptions for each skill.
    """
    if not jobs:
        return {}
    agg = {s: 0.0 for s in CANONICAL_SKILLS}
    for j in jobs:
        scores = hybrid_skill_scores(j.get("description", ""))
        for s in CANONICAL_SKILLS:
            agg[s] += scores.get(s, 0.0)
    n = float(len(jobs))
    return {s: (agg[s] / n) for s in CANONICAL_SKILLS}

# -------- Main analysis: resume vs jobs --------
def skill_gap_analysis(resume_text: str, job_query: str, num_jobs: int = 10,
                       job_threshold: float = 0.40) -> List[Dict]:
    """
    Returns a sorted list of dict rows:
      {"skill", "resume_score", "job_score", "gap"}
    Sorted by descending gap (bigger gap = more missing).
    Only includes skills where job_score >= job_threshold.
    """
    resume_scores = hybrid_skill_scores(resume_text)
    jobs = fetch_jobs_remotive(job_query, limit=num_jobs)
    job_scores = aggregate_job_skill_scores(jobs)

    rows = []
    for s in CANONICAL_SKILLS:
        r = resume_scores.get(s, 0.0)
        j = job_scores.get(s, 0.0)
        gap = j - r
        if j >= job_threshold and gap > 0.05:
            rows.append({"skill": s, "resume_score": round(r, 3),
                         "job_score": round(j, 3), "gap": round(gap, 3)})
    rows.sort(key=lambda x: (-x["gap"], -x["job_score"], x["skill"]))
    return rows
