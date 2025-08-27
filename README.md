# JobSkills Detector

Final project for **Duke AIPI-503 Python Bootcamp**.  
The goal of the project is to detect technical skills from resumes or job text using Python.  

---

## Features
- Detects skills from either:
  - **pasted text**  
  - **uploaded PDF resumes**  
- Uses a keyword list of common technical skills (Python, SQL, Pandas, NumPy, scikit-learn, Tableau, Git, Excel, etc.).  
- Provides both a **web app** (built with Streamlit) and a **command line tool (CLI)**.  
- Simple output: prints out which skills were detected.  

---

## Tech Stack
- Python 3.9+  
- Streamlit  
- pypdf (for reading PDFs)  
- pandas / numpy / scikit-learn  

---

## How to Run the Streamlit App

1. **Clone this repo**  
bash:
git clone https://github.com/SophiaYifei/503-Python-Bootcamp-Final-Project.git
cd 503-Python-Bootcamp-Final-Project

2. **Set up the Environment**  
python3 -m venv project-env
source project-env/bin/activate

3. **Install Requirements** 
pip install -r requirements.txt

4. **Run Streamlit** 
streamlit run app.py

---

## How to Run the CLI Version
# --- Skill detection from direct text ---
# This runs the CLI in "skills" mode.
# It takes a text string (resume snippet or self-description)
# and outputs the top 10 skills with similarity scores (0–1).
python cli_demo.py --mode skills --text "I have Python, Pandas and AWS experience." --top-k 10

## --- Gap analysis: resume file vs. job postings ---
# This runs the CLI in "gap" mode.
# --resume: path to your resume file (PDF or TXT).
# --job-query: keyword(s) to search job postings from the Remotive API.
# --num-jobs: how many job postings to analyze (e.g., 8 means average across 8 postings).
# --top-k: show only the top 10 skills with the largest demand gaps.
# The output lists skills that are emphasized in job postings
# but not strongly reflected in the resume (gap = job_score − resume_score).
python cli_demo.py --mode gap --resume "path\to\resume.pdf" --job-query "data scientist" --num-jobs 8 --top-k 10

1. **Manual Text Input**
Bash:
python cli_demo.py --text "I have experience with Python, SQL, and Tableau."

# Python Version

This project was built and tested with:

Python 3.9+

## Hugging Face Space

# Project Structure
├── app.py            # Streamlit app
├── api.py            # API logic
├── cli_demo.py       # CLI demo runner
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation
└── resume.jpg        # image

![Demo Screenshot](resume.jpg)




