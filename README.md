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
- Python 3.10+  
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

## How to Run the CLU Version

1. **Manual Text Input**
Bash:
python cli_demo.py --text "I have experience with Python, SQL, and Tableau."

2. **Read from PDF**
Bash:
python cli_demo.py --pdf path/to/Resume.pdf

