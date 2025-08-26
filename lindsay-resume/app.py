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

# ---------------- Sidebar inputs ----------------
with st.sidebar:
    st.header("Inputs")
    uploaded = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
    job_query = st.text_input("Job search (Remotive):", placeholder="e.g., data scientist, ML engineer")
    num_jobs = st.slider("Number of job postings to analyze", 3, 30, 10)
    job_threshold = st.slider(
        "Skill importance threshold (jobs)", 0.0, 1.0, 0.40, 0.05,
        help="Only show skills that the job postings emphasize at least this much."
    )
    show_jobs = st.checkbox("Preview fetched job postings", value=False)
    show_resume_scores = st.checkbox("Preview resume skill scores", value=False)

colA, colB = st.columns([1, 2])

# ---------------- Load resume text ----------------
resume_text = ""
if uploaded is not None:
    file_bytes = uploaded.read()
    resume_text = extract_text_from_file(uploaded.name, file_bytes)
else:
    with colA:
        st.info("Upload a resume (PDF/TXT) on the left to begin.")

# ---------------- Main analysis ----------------
if resume_text and job_query.strip():
    with st.spinner("Analyzing skills with local MiniLM embeddings…"):
        rows = skill_gap_analysis(
            resume_text, job_query, num_jobs=num_jobs, job_threshold=job_threshold
        )
        df = pd.DataFrame(rows) if rows else pd.DataFrame(
            columns=["skill", "resume_score", "job_score", "gap"]
        )

    if df.empty:
        st.warning(
            "No clear skill gaps found. Try increasing the number of jobs, "
            "lowering the threshold, or using a broader query."
        )
    else:
        # ---- Chart ----
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

        # ---- Table + download ----
        with colB:
            st.subheader("Details (table)")
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "Download CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="skill_gaps.csv",
                mime="text/csv",
            )

        # ---- Debug / previews ----
        with st.expander("Why these results? (debug previews)"):
            # Resume scores preview
            if show_resume_scores:
                st.write("**Resume skill scores (0–1, higher = stronger evidence):**")
                resume_scores = hybrid_skill_scores(resume_text)
                rdf = pd.DataFrame(
                    [{"skill": k, "score": round(v, 3)} for k, v in resume_scores.items()]
                ).sort_values("score", ascending=False)
                st.dataframe(rdf, use_container_width=True, hide_index=True)

            # Job results (clickable list + filters + CSV)
            if show_jobs:
                st.write("**Job results (from Remotive):**")
                jobs = fetch_jobs_remotive(job_query, limit=num_jobs)

                if not jobs:
                    st.info("No jobs returned for this search.")
                else:
                    kw = st.text_input("Filter by keyword (title/company/location):", "")
                    max_desc = st.slider("Max description length (chars)", 120, 1000, 300, 20)
                    show_table = st.checkbox("Show compact table view", value=False)

                    # keyword filter
                    if kw.strip():
                        k = kw.lower()
                        jobs = [
                            j for j in jobs
                            if (k in j.get("title","").lower()
                                or k in j.get("company","").lower()
                                or k in j.get("location","").lower())
                        ]

                    jobs_df = pd.DataFrame(
                        jobs, columns=["title", "company", "location", "date", "url", "description"]
                    )
                    st.download_button(
                        "Download jobs CSV",
                        data=jobs_df.to_csv(index=False).encode("utf-8"),
                        file_name="jobs.csv",
                        mime="text/csv",
                    )

                    if show_table:
                        st.dataframe(
                            jobs_df.drop(columns=["description"]),
                            use_container_width=True, hide_index=True
                        )
                    else:
                        for j in jobs:
                            title = j.get("title", "")
                            url = j.get("url", "")
                            company = j.get("company", "")
                            location = j.get("location", "")
                            date = j.get("date", "")
                            desc = j.get("description", "")
                            st.markdown(
                                f"### [{title}]({url})  \n"
                                f"**{company}** • {location} • {date}"
                            )
                            preview = desc[:max_desc] + ("…" if len(desc) > max_desc else "")
                            st.caption(preview)
                            st.divider()

else:
    st.caption("Tip: upload your resume and enter a job search like “data analyst” or “ML engineer”.")
