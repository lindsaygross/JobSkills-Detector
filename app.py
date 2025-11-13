import requests
import streamlit as st
import pandas as pd
import altair as alt

from api import extract_text_from_file, skill_gap_analysis

st.set_page_config(page_title="Resume → Job Skill Gap", page_icon="🧩", layout="wide")

SAMPLE_RESUME = """
Avery Parker
Data Scientist | Raleigh, NC | avery.parker@email.com

SUMMARY
Data scientist with 6+ years of experience shaping analytics roadmaps, building ML products, and partnering with GTM leaders.

EXPERIENCE
- Built SQL + dbt powered lakehouse, improving marketing attribution accuracy by 24%.
- Trained scikit-learn churn models with SHAP insights that cut enterprise churn by 9%.
- Productionized NLP topic modeling on AWS (S3, Lambda, SageMaker) to surface customer intent.
- Mentored 3 analysts on Python, Airflow, Tableau, and stakeholder storytelling.

TOOLS
Python, Pandas, NumPy, SQL, Snowflake, DBT, Airflow, Tableau, Docker, AWS (S3, Lambda, Redshift)
""".strip()

CUSTOM_STYLE = """
<style>
:root {
    --accent-primary: #6c63ff;
    --accent-secondary: #f3f0ff;
    --text-muted: #6b7280;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
}
.hero-card {
    background: linear-gradient(135deg, var(--accent-primary), #a38bff);
    color: white;
    padding: 1.2rem 1.4rem;
    border-radius: 16px;
    box-shadow: 0 12px 30px rgba(108, 99, 255, 0.25);
}
.hero-label {
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-size: 0.75rem;
    margin-bottom: 0.3rem;
    opacity: 0.8;
}
.hero-card ul {
    padding-left: 1rem;
    margin-bottom: 0;
}
.status-card {
    padding: 0.9rem 1rem;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    background: #fff;
}
.metric-highlight {
    padding: 0.75rem 1rem;
    border-radius: 12px;
    background: var(--accent-secondary);
    color: var(--accent-primary);
    font-weight: 600;
}
</style>
"""
st.markdown(CUSTOM_STYLE, unsafe_allow_html=True)

hero_left, hero_right = st.columns([3, 2])
with hero_left:
    st.title("🧩 Resume → Job Skill Gap")
    st.markdown(
        "Upload a resume (PDF/TXT) or paste raw text, pair it with a job search, "
        "and instantly see which technical skills recruiters emphasize most."
    )
with hero_right:
    st.markdown(
        """
        <div class="hero-card">
            <p class="hero-label">Quick start</p>
            <ul>
                <li>Upload or paste your resume text</li>
                <li>Search any job title or keyword</li>
                <li>Explore missing skills, resume signals, and live postings</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()

with st.sidebar:
    st.header("Resume")
    uploaded = st.file_uploader("Upload PDF or TXT file", type=["pdf", "txt"])
    manual_text = st.text_area(
        "Or paste resume text",
        placeholder="Paste your resume text here…",
        height=180,
    )
    use_sample = st.checkbox(
        "Use sample resume",
        help="Loads a built-in sample so you can explore the UI without a file.",
    )
    st.divider()
    st.header("Job Search")
    job_query = st.text_input(
        "Job search (Remotive)",
        placeholder="e.g., data scientist, ML engineer",
    )
    preferred_location = st.text_input(
        "Preferred location (optional)",
        placeholder="e.g., Remote, New York, Europe",
    )
    num_jobs = st.slider("Number of jobs to analyze", 3, 30, 12)
    job_threshold = st.slider(
        "Skill importance threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.40,
        step=0.05,
        help="Only show gaps where job postings score at or above this level (0–1).",
    )

resume_text = ""
resume_source = ""
if uploaded is not None:
    file_bytes = uploaded.read()
    resume_text = extract_text_from_file(uploaded.name, file_bytes)
    resume_source = f"Uploaded file • {uploaded.name}"
elif manual_text and manual_text.strip():
    resume_text = manual_text.strip()
    resume_source = "Manual text input"
elif use_sample:
    resume_text = SAMPLE_RESUME
    resume_source = "Sample resume"

job_query_clean = job_query.strip()

status_col1, status_col2 = st.columns(2)
with status_col1:
    if resume_text:
        st.markdown(f"<div class='status-card'>✅ Resume ready — {resume_source}</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='status-card'>⚠️ Add a resume: upload, paste text, or toggle the sample.</div>",
            unsafe_allow_html=True,
        )
with status_col2:
    if job_query_clean:
        loc_snippet = ""
        if preferred_location.strip():
            loc_snippet = f"<br><span style='color: var(--text-muted);'>Pref: {preferred_location.strip()}</span>"
        st.markdown(
            f"<div class='status-card'>🔍 Job query — <strong>{job_query_clean}</strong>{loc_snippet}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='status-card'>💡 Enter a job title or skill to pull live postings.</div>",
            unsafe_allow_html=True,
        )

if not resume_text or not job_query_clean:
    st.info(
        "Provide both a resume and a job search to unlock the full analysis. "
        "Need inspiration? Try the sample resume with “data scientist”."
    )
    st.stop()

try:
    rows, resume_scores, job_scores, jobs = skill_gap_analysis(
        resume_text,
        job_query_clean,
        num_jobs=num_jobs,
        job_threshold=job_threshold,
        preferred_location=preferred_location,
        return_metadata=True,
    )
except requests.exceptions.RequestException:
    st.error("Unable to fetch jobs from Remotive right now. Please try again in a moment.")
    st.stop()

df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["skill", "resume_score", "job_score", "gap"])
gap_count = len(df)
avg_gap = float(df["gap"].mean()) if not df.empty else 0.0
jobs_analyzed = len(jobs)

summary_container = st.container()
summary_container.subheader("Insight snapshot")
m1, m2, m3 = summary_container.columns(3)
m1.metric("Gaps detected", gap_count)
m2.metric("Avg gap size", f"{avg_gap:.2f}")
m3.metric("Jobs analyzed", jobs_analyzed)
if not df.empty:
    top_skill = df.iloc[0]["skill"]
    top_gap = df.iloc[0]["gap"]
    summary_container.markdown(
        f"<p class='metric-highlight'>Top gap: {top_skill} (gap {top_gap:.2f})</p>",
        unsafe_allow_html=True,
    )
elif jobs_analyzed == 0:
    summary_container.warning(
        "Remotive did not return any jobs for this query. Try a broader search or fewer filters."
    )
else:
    summary_container.success(
        "Nice! No critical skill gaps were detected at the current threshold."
    )

tab_jobs, tab_gaps, tab_resume = st.tabs(["Job explorer", "Skill gaps", "Resume signals"])

with tab_jobs:
    st.markdown("### Live job explorer")
    st.caption("Job data powered by [remotive.com](https://remotive.com/).")
    if preferred_location.strip():
        st.caption(f"Filtering to locations that include “{preferred_location.strip()}”.")
    if not jobs:
        st.warning("No job postings returned for this search.")
    else:
        filter_col, mode_col = st.columns([2, 1])
        kw = filter_col.text_input("Filter by keyword", key="job_filter")
        view_mode = mode_col.radio("View", ["Cards", "Table"], horizontal=True)
        max_desc = st.slider("Max description length (characters)", 120, 1000, 320, 20)

        job_list = jobs
        if kw and kw.strip():
            k = kw.lower().strip()
            job_list = [
                j
                for j in job_list
                if (
                    k in j.get("title", "").lower()
                    or k in j.get("company", "").lower()
                    or k in j.get("location", "").lower()
                )
            ]

        jobs_df = pd.DataFrame(
            job_list,
            columns=["title", "company", "location", "date", "url", "description"],
        )
        st.download_button(
            "Download jobs CSV",
            data=jobs_df.to_csv(index=False).encode("utf-8"),
            file_name="jobs.csv",
            mime="text/csv",
        )

        if job_list and view_mode == "Table":
            st.dataframe(
                jobs_df.drop(columns=["description"]),
                use_container_width=True,
                hide_index=True,
            )
        elif job_list:
            for j in job_list:
                title = j.get("title", "")
                url = j.get("url", "")
                company = j.get("company", "")
                location = j.get("location", "")
                date = j.get("date", "")
                desc = j.get("description", "")
                preview = desc[:max_desc] + ("…" if len(desc) > max_desc else "")
                st.markdown(f"#### [{title}]({url})")
                st.caption(f"{company} • {location} • {date}")
                st.write(preview)
                st.divider()
        else:
            st.info("No jobs matched the filter.")

with tab_gaps:
    st.markdown("### Where to focus first")
    if df.empty:
        st.info(
            "No clear gaps surfaced. Consider increasing the number of jobs, lowering the threshold, "
            "or choosing a more general query."
        )
    else:
        chart = (
            alt.Chart(df.head(20))
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("gap:Q", title="Gap (job emphasis − resume evidence)"),
                y=alt.Y("skill:N", sort="-x", title="Skill"),
                color=alt.Color(
                    "gap:Q",
                    scale=alt.Scale(range=["#c7d2fe", "#6c63ff"]),
                    legend=None,
                ),
                tooltip=["skill", "resume_score", "job_score", "gap"],
            )
        )
        st.altair_chart(chart, use_container_width=True)

        st.markdown("### Detailed table")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="skill_gaps.csv",
            mime="text/csv",
        )

with tab_resume:
    st.markdown("### Resume skill signals")
    if not resume_scores:
        st.info("No resume skills detected.")
    else:
        resume_df = (
            pd.DataFrame(
                [{"skill": k, "score": round(v, 3)} for k, v in resume_scores.items()]
            )
            .sort_values("score", ascending=False)
            .reset_index(drop=True)
        )
        max_rows = len(resume_df)
        slider_min = 1
        slider_default = min(10, max_rows)
        top_n = st.slider(
            "Show top N skills",
            slider_min,
            max_rows,
            slider_default,
        )
        st.dataframe(resume_df.head(top_n), use_container_width=True, hide_index=True)
        st.caption(
            "Scores combine local MiniLM embeddings with keyword hits. "
            "Higher numbers mean stronger resume evidence."
        )

if resume_text:
    with st.expander("Peek at the processed resume text (for debugging)"):
        st.write(resume_text[:4000] + ("…" if len(resume_text) > 4000 else ""))
