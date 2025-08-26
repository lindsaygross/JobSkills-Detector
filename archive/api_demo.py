from __future__ import annotations
from typing import List, Dict, Any, Iterable
import os
import re

DEMO_MODE = True  # True = Run through the UI with very simple placeholder logic; False = Throw an error and wait for teammates to implement.

# The standard skill list for teammates is optional: If they have a larger vocabulary/model, it is not mandatory here
DEMO_VOCAB = {
    "python","sql","excel","tableau","pandas","power bi","r","aws","git","spark",
    "docker","linux","rest apis","numpy","scikit-learn","sklearn"
}

def detect_skills(text: str, threshold: float = 0.4) -> List[str]:
    """
    CONTRACT:
        Input:  free-text string; threshold in [0,1].
        Output: list of skill strings (unique, case-insensitive).
    To be implemented by teammates using HF embeddings + cosine similarity.

    Temporary behavior (DEMO_MODE=True):
        - simple vocab-based matching to let the UI run.
    """
    if not DEMO_MODE:
        raise NotImplementedError("detect_skills() is not implemented yet.")

    tokens = re.findall(r"[A-Za-z0-9#+.]+", text.lower())
    # join tokens to allow "power bi"
    joined = " ".join(tokens)
    found = []
    seen = set()
    for s in DEMO_VOCAB:
        if s in joined and s not in seen:
            found.append(s)
            seen.add(s)
    return found

def extract_text_from_pdf(file) -> str:
    """
    CONTRACT:
        Input:  a file-like object from st.file_uploader
        Output: extracted plain text
    To be implemented by teammates (e.g., with pypdf).
    """
    if not DEMO_MODE:
        raise NotImplementedError("extract_text_from_pdf() is not implemented yet.")
    return ""  # demo: return empty → UI will notify that no text was extracted


def compute_demand(job_posts: Iterable[Dict[str, str]], threshold: float = 0.4) -> Dict[str, int]:
    """
    CONTRACT:
        Input:  iterable of dicts: {"title": str, "description": str}
        Output: dict {skill -> demand_count}
    To be implemented by teammates (call detect_skills on each concatenated text).
    """
    if not DEMO_MODE:
        raise NotImplementedError("compute_demand() is not implemented yet.")
    # demo implementation
    counts = {}
    for p in job_posts:
        text = f"{p.get('title','')} {p.get('description','')}"
        present = detect_skills(text, threshold=threshold)
        for s in present:
            counts[s] = counts.get(s, 0) + 1
    return counts

def summarize(demand_counts: Dict[str,int], resume_skills: Iterable[str], total_posts: int) -> "Any":
    """
    CONTRACT:
        Input:
          - demand_counts: {skill -> count}
          - resume_skills: iterable of skill strings
          - total_posts: int
        Output:
          - pandas.DataFrame with columns: [skill, demand_count, demand_pct, in_resume]
    To be implemented by teammates (pandas/DataFrame).
    """
    try:
        import pandas as pd
    except Exception:
        raise RuntimeError("pandas not available; add to requirements.txt")

    rows = []
    resume_set = set(map(str.lower, resume_skills or []))
    for s, c in (demand_counts or {}).items():
        pct = round(100 * c / max(total_posts, 1), 1)
        rows.append({
            "skill": s,
            "demand_count": c,
            "demand_pct": pct,
            "in_resume": s.lower() in resume_set
        })
    df = pd.DataFrame(rows).sort_values(["demand_count", "skill"], ascending=[False, True])
    return df
