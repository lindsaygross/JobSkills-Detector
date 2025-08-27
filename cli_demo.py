# cli_demo.py
# Command-line demo for our API layer.
# Modes:
#   - skills: detect skills from --text or --resume (PDF/TXT)
#   - gap:    compute resume→job skill gap with --job-query

import os
import argparse
from typing import List, Dict
from api import (
    extract_text_from_file,
    hybrid_skill_scores,
    skill_gap_analysis,
)

def read_resume(path: str) -> str:
    """Read a PDF/TXT file and return extracted plain text."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Resume file not found: {path}")
    with open(path, "rb") as f:
        data = f.read()
    return extract_text_from_file(os.path.basename(path), data)

def run_skills(text: str, top_k: int):
    """Print top-K skills with scores from 0–1."""
    scores = hybrid_skill_scores(text)
    if not scores:
        print("No skills detected.")
        return
    items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    if top_k > 0:
        items = items[:top_k]
    print("\nTop skills (score in 0–1):")
    for k, v in items:
        print(f"  - {k:15s}  {v:.3f}")

def run_gap(text: str, job_query: str, num_jobs: int, job_threshold: float, top_k: int):
    """Print top-K missing skills based on job demand minus resume evidence."""
    rows = skill_gap_analysis(
        resume_text=text,
        job_query=job_query,
        num_jobs=num_jobs,
        job_threshold=job_threshold,
    )
    if not rows:
        print("No clear gaps found. Try a broader query or lower threshold.")
        return
    if top_k > 0:
        rows = rows[:top_k]
    print("\nTop missing skills (gap = job_score - resume_score):")
    for r in rows:
        print(f"  - {r['skill']:15s}  resume={r['resume_score']:.3f}  "
              f"job={r['job_score']:.3f}  gap={r['gap']:.3f}")

def main():
    p = argparse.ArgumentParser(
        description="CLI demo for Resume → Job Skill analysis"
    )
    p.add_argument("--mode", choices=["skills", "gap"], default="skills",
                   help="skills: detect from text/resume; gap: compute resume→job gaps")
    p.add_argument("--text", type=str, default="",
                   help="Direct text input (if provided, overrides --resume)")
    p.add_argument("--resume", type=str, default="",
                   help="Path to a PDF or TXT resume")
    p.add_argument("--top-k", type=int, default=10,
                   help="Show top-K results (use 0 to show all)")

    # gap-specific
    p.add_argument("--job-query", type=str, default="",
                   help="Job search query, e.g., 'data scientist'")
    p.add_argument("--num-jobs", type=int, default=10,
                   help="Number of job postings to analyze")
    p.add_argument("--job-threshold", type=float, default=0.40,
                   help="Only consider skills with job_score ≥ this threshold (0–1)")

    args = p.parse_args()

    # Prepare resume text (text overrides file if both provided)
    resume_text = args.text.strip()
    if not resume_text and args.resume:
        resume_text = read_resume(args.resume)

    if args.mode == "skills":
        if not resume_text:
            raise SystemExit("Please provide --text or --resume for skills mode.")
        run_skills(resume_text, top_k=args.top_k)

    elif args.mode == "gap":
        if not resume_text:
            raise SystemExit("Please provide --text or --resume for gap mode.")
        if not args.job_query.strip():
            raise SystemExit("Please provide --job-query for gap mode.")
        run_gap(
            text=resume_text,
            job_query=args.job_query.strip(),
            num_jobs=args.num_jobs,
            job_threshold=args.job_threshold,
            top_k=args.top_k,
        )

if __name__ == "__main__":
    main()
