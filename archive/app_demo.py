import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from api import (
    detect_skills,
    extract_text_from_pdf,
    compute_demand,
    summarize,
)

st.set_page_config(page_title="Skill Detector", page_icon="🧰", layout="wide")
st.title("🧰 Resume & Job Skill Analyzer")
st.caption(
    "Paste text or upload a PDF to extract skills, and compare with job postings. "
    "Left sidebar controls visualization and similarity threshold."
)

# ----- Sidebar controls -----
threshold = st.sidebar.slider("Similarity threshold", 0.0, 1.0, 0.40, 0.01)
display = st.sidebar.selectbox("Display", ["Bar chart", "Table"])
top_n = st.sidebar.number_input("Top-N to show (0=all)", 0, 200, 0, step=1)
dedup = st.sidebar.checkbox("Deduplicate", value=True)

def postprocess(skills: list[str]) -> list[str]:
    if not skills:
        return []
    # lower → unique → restore as typed (here kept lower)
    seen, out = set(), []
    for s in skills:
        s2 = s.strip()
        if not s2:
            continue
        key = s2.lower()
        if dedup and key in seen:
            continue
        out.append(s2)
        seen.add(key)
    if top_n > 0:
        out = out[:top_n]
    return out

def render_skill_tags(skills: list[str]):
    if not skills:
        st.warning("No skills found.")
        return
    tags = " ".join([f"`{s}`" for s in skills])
    st.markdown(f"**Detected skills ({len(skills)}):** {tags}")

def render_chart_or_table(df: pd.DataFrame, title: str):
    st.subheader(title)
    if df is None or df.empty:
        st.info("No data to display.")
        return
    if display == "Table":
        st.dataframe(df)
    else:
        # If df has ['skill','count'] or ['category','count'] like columns
        x_col = None
        y_col = None
        for cand in ["skill","category","name","label"]:
            if cand in df.columns:
                x_col = cand
                break
        for cand in ["count","demand_count","value","score"]:
            if cand in df.columns:
                y_col = cand
                break
        if x_col is None or y_col is None:
            st.dataframe(df)
            return
        fig, ax = plt.subplots()
        ax.bar(df[x_col], df[y_col])
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(title)
        st.pyplot(fig)

def download_df(df: pd.DataFrame, filename: str):
    if df is None or df.empty:
        return
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, file_name=filename, mime="text/csv")

# ----- Tabs -----
tab1, tab2, tab3 = st.tabs(["Paste Text", "Upload PDF", "Job Postings"])

with tab1:
    t = st.text_area("Paste resume or job text:", height=220)
    if st.button("Detect skills from text", type="primary", use_container_width=True):
        with st.spinner("Detecting..."):
            try:
                skills = detect_skills(t or "", threshold=threshold)
            except NotImplementedError:
                st.error("detect_skills() not implemented yet. Ask the API teammate to wire it up.")
                skills = []
            except Exception as e:
                st.error(f"Error: {e}")
                skills = []
        skills = postprocess(skills)
        render_skill_tags(skills)
        if skills:
            df_present = pd.DataFrame({"skill": skills, "count": 1})
            render_chart_or_table(df_present, "Skills found")

with tab2:
    up = st.file_uploader("Upload a PDF resume or JD", type=["pdf"])
    if st.button("Detect skills from PDF", use_container_width=True):
        text_pdf = ""
        with st.spinner("Parsing PDF..."):
            try:
                text_pdf = extract_text_from_pdf(up) if up else ""
            except NotImplementedError:
                st.error("extract_text_from_pdf() not implemented yet. PDF reading is assigned to a teammate.")
            except Exception as e:
                st.error(f"PDF error: {e}")
        if text_pdf:
            with st.spinner("Detecting..."):
                try:
                    skills = detect_skills(text_pdf, threshold=threshold)
                except NotImplementedError:
                    st.error("detect_skills() not implemented yet.")
                    skills = []
                except Exception as e:
                    st.error(f"Error: {e}")
                    skills = []
            skills = postprocess(skills)
            render_skill_tags(skills)
            if skills:
                df_present = pd.DataFrame({"skill": skills, "count": 1})
                render_chart_or_table(df_present, "Skills found")

with tab3:
    st.write("Provide multiple job postings (JSON list or one posting per line: 'Title :: Description').")
    jobs_text = st.text_area("Job postings input:", height=180,
        placeholder='e.g.\nData Analyst :: Analyze data using Python, SQL, Excel. Build Tableau dashboards.\nML Engineer :: Work with Scikit-learn, Spark, AWS. Knowledge of Git.\nBI Analyst :: Create Power BI dashboards. SQL required.')
    if st.button("Analyze demand", use_container_width=True):
        # parse to list[dict]
        posts = []
        raw = jobs_text.strip()
        if raw.startswith("[") and raw.endswith("]"):
            import json
            try:
                posts = json.loads(raw)
            except Exception as e:
                st.error(f"JSON parse error: {e}")
        else:
            for line in raw.splitlines():
                if "::" in line:
                    title, desc = line.split("::", 1)
                    posts.append({"title": title.strip(), "description": desc.strip()})
                elif line.strip():
                    posts.append({"title": "", "description": line.strip()})

        if not posts:
            st.warning("No valid postings parsed.")
        else:
            with st.spinner("Computing demand..."):
                try:
                    counts = compute_demand(posts, threshold=threshold)
                except NotImplementedError:
                    st.error("compute_demand() not implemented yet. Assigned to API teammate.")
                    counts = {}
                except Exception as e:
                    st.error(f"Error: {e}")
                    counts = {}
            if counts:
                df_counts = pd.DataFrame(
                    sorted(counts.items(), key=lambda x: (-x[1], x[0])),
                    columns=["skill","demand_count"]
                )
                render_chart_or_table(df_counts, "Skill demand across postings")
                download_df(df_counts, "skill_demand.csv")

            # Optional: compare with a pasted resume text from tab1 if available
            if t:
                try:
                    resume_sk = detect_skills(t, threshold=threshold)
                except Exception:
                    resume_sk = []
                df_sum = summarize(counts, resume_sk, len(posts))
                st.subheader("Resume vs. Demand (summary)")
                st.dataframe(df_sum)
                # show top missing
                missing = df_sum[(df_sum["in_resume"] == False) & (df_sum["demand_count"] > 0)]
                st.write("**Top missing skills:**")
                st.dataframe(missing.sort_values("demand_count", ascending=False).head(5))
                download_df(df_sum, "resume_vs_demand.csv")
