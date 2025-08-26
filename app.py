import streamlit as st
from api import detect_skills, extract_text_from_pdf_bytes

st.title("Skill Detector")
text = st.text_area("Paste your text:")

uploaded = st.file_uploader("...or upload a PDF resume", type=["pdf"])
if uploaded is not None:
    pdf_text = extract_text_from_pdf_bytes(uploaded.read())
    st.caption(f"Extracted {len(pdf_text)} characters from PDF")
    text = (text or "") + "\n" + (pdf_text or "")

if text:
    st.write("Detected skills:", detect_skills(text))
