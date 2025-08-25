# app.py
import streamlit as st
import pandas as pd
import altair as alt

from api import (
    extract_text_from_file,
    skill_gap_analysis,
    hybrid_skill_scores,
    fetch_jobs_remotive,
)

st.set_page_config(page_title="Resume → Job Skill Gap", page_icon="🧩", layout="wide")
st.title("🧩 Resume → Job Skill Gap (local embeddings + free jobs API)")

with st.sidebar:
    st.header("Inputs")
    uploaded = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
    job_query = st.text_input("Job search (Remotive):", placeholder="e.g., data scientist, ML engineer")
    num_jobs = st.slider("Number of job postings to analyze", 3, 30, 10)
    job_threshold = st.slider("Skill importance threshold (jobs)", 0.0, 1.0, 0.40, 0.05,
                              help="Only show skills that the job postings emphasize at least this much.")
    show_jobs = st.checkbox("Preview fetched job postings", value=False)
    show_resume_scores = st.checkbox("Preview resume skill scores", value=False)

colA, colB = st.columns([1, 2])

resume_text = ""
if uploaded is not None:
    file_bytes = uploaded.read()
    resume_text = extract_text_from_file(uploaded.name, file_bytes)
else:
    with colA:
        st.info("Upload a resume (PDF/TXT) on the left to begin.")

# Run analysis
if resume_text and job_query.strip():
    with st.spinner("Analyzing skills with local MiniLM embeddings…"):
        rows = skill_gap_analysis(resume_text, job_query, num_jobs=num_jobs, job_threshold=job_threshold)
        df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["skill", "resume_score", "job_score", "gap"])

    if df.empty:
        st.warning("No clear skill gaps found. Try increasing the number of jobs, lowering the threshold, or using a broader query.")
    else:
        with colA:
            st.subheader("Top missing skills")
            st.caption("Gap = Job emphasis − Resume evidence (0–1).")
            chart = (
                alt.Chart(df.head(20))
                .mark_bar()
                .encode(
                    x=alt.X("gap:Q", title="Gap (missing)"),
                    y=alt.Y("skill:N", sort="-x", title="Skill"),
                    tooltip=["skill", "resume_score", "job_score", "gap"],
                )
            )
            st.altair_chart(chart, use_container_width=True)

        with colB:
            st.subheader("Details (table)")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "Download CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="skill_gaps.csv",
                mime="text/csv",
            )

        with st.expander("Why these results? (debug previews)"):
            if show_resume_scores:
                st.write("**Resume skill scores (0–1, higher = stronger evidence):**")
                resume_scores = hybrid_skill_scores(resume_text)
                rdf = pd.DataFrame(
                    [{"skill": k, "score": round(v, 3)} for k, v in resume_scores.items()]
                ).sort_values("score", ascending=False)
                st.dataframe(rdf, use_container_width=True, hide_index=True)

            if show_jobs:
                st.write("**Sample fetched jobs (first few):**")
                jobs = fetch_jobs_remotive(job_query, limit=min(5, num_jobs))
                for j in jobs:
                    st.markdown(f"**{j['title']}** — {j['company']}")
                    st.caption(j["description"][:500] + ("…" if len(j["description"]) > 500 else ""))

else:
    st.caption("Tip: upload your resume and enter a job search like “data analyst” or “ML engineer”.")
