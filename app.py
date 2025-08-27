import streamlit as st
from api import detect_skills, extract_text_from_pdf_bytes

st.title("Skill Detector")

# Text input
text = st.text_area("Paste your text:")

# PDF upload
uploaded_file = st.file_uploader("...or upload a PDF resume", type="pdf")

if uploaded_file is not None:
    # Read PDF bytes and extract text
    file_bytes = uploaded_file.read()
    pdf_text = extract_text_from_pdf_bytes(file_bytes)
    st.info(f"Extracted {len(pdf_text)} characters from PDF")
    text = pdf_text  # override text with PDF content

# Show detected skills
if text:
    skills = detect_skills(text)
    if skills:
        st.success("Detected skills: " + ", ".join(skills))
    else:
        st.warning("No skills detected in the text.")
