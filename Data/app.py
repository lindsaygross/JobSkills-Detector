import streamlit as st
from api import detect_skills

st.title("Skill Detector")
text = st.text_area("Paste your text:")
if text:
    st.write("Detected skills:", detect_skills(text))
