#Imports
import streamlit as st
from api import detect_skills, extract_text_from_pdf_bytes
#Title
st.title("Skill Detector")
#Text Input
text = st.text_area("Paste your text:")
#PDF Upload 
uploaded = st.file_uploader("...or upload a PDF resume", type=["pdf"])
if uploaded is not None:
    pdf_text = extract_text_from_pdf_bytes(uploaded.read())
    st.caption(f"Extracted {len(pdf_text)} characters from PDF")
    text = (text or "") + "\n" + (pdf_text or "")
#Show detected skills
if text:
    skills = detect_skills(text)
    if skills:
        st.success("Detected skills: " + ", ".join(skills))
    else:
        st.warning("No skills detected in the text.")
