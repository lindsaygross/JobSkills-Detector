# app.py
import streamlit as st
import pandas as pd
import altair as alt
from api import detect_skills

st.set_page_config(page_title="Skill Detector", page_icon="🧠", layout="centered")
st.title("🧠 Skill Detector")

st.write("Paste text (resume, job post, notes) and I’ll extract skills, count them, and visualize the results.")

# --- Inputs ---
text = st.text_area("Paste your text here:", height=180, placeholder="e.g., I build apps with Python, Pandas, NumPy, Streamlit, and scikit-learn.")
view = st.selectbox("How do you want to view results?", ["Table", "Bar chart"])
min_count = st.slider("Minimum count to display", 1, 5, 1, help="Hide rarely-mentioned skills")
show_download = st.checkbox("Enable CSV download")

# --- Core logic ---
def normalize_to_counts(skills_output):
    """
    Accepts output as list[str] OR dict[str,int] OR set[str]
    and returns a DataFrame with columns: skill, count
    """
    if not skills_output:
        return pd.DataFrame(columns=["skill", "count"])

    if isinstance(skills_output, dict):
        df = pd.DataFrame(list(skills_output.items()), columns=["skill", "count"])
    else:
        # list or set -> count
        items = list(skills_output) if isinstance(skills_output, set) else skills_output
        s = pd.Series([str(x).strip() for x in items if str(x).strip()])
        df = s.value_counts().rename_axis("skill").reset_index(name="count")

    # filter by slider
    return df[df["count"] >= min_count].sort_values(["count", "skill"], ascending=[False, True]).reset_index(drop=True)

if text.strip():
    raw = detect_skills(text)
    df = normalize_to_counts(raw)

    if df.empty:
        st.info("No skills detected yet. Try adding more specific technologies or keywords.")
    else:
        st.subheader("Detected skills")
        st.caption(f"{int(df['count'].sum())} total mentions across {len(df)} unique skills (after filtering).")

        if view == "Table":
            st.dataframe(df, use_container_width=True)
        else:
            chart = (
                alt.Chart(df)
                .mark_bar()
                .encode(
                    x=alt.X("skill:N", sort="-y", title="Skill"),
                    y=alt.Y("count:Q", title="Count"),
                    tooltip=["skill", "count"]
                )
            )
            st.altair_chart(chart, use_container_width=True)

        if show_download:
            st.download_button(
                "Download CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="skills_detected.csv",
                mime="text/csv",
            )
else:
    st.caption("Tip: mention specific tools (Python, pandas, NumPy, Streamlit, scikit-learn, SQL, AWS, etc.)")
