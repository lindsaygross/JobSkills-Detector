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

python cli_demo.py --mode skills --text "I have Python, Pandas and AWS experience." --top-k 10

## --- Gap analysis: resume file vs. job postings ---
python cli_demo.py --mode gap --resume "path\to\resume.pdf" --job-query "data scientist" --num-jobs 8 --top-k 10

1. **Manual Text Input**
Bash:
python cli_demo.py --text "I have experience with Python, SQL, and Tableau."

# Python Version

This project was built and tested with:

Python 3.9+

## Hugging Face Space
https://huggingface.co/spaces/Lindsaygross/jobskills

# Project Structure
.
├── app.py            # Streamlit app  
├── api.py            # API logic  
├── cli_demo.py       # CLI demo runner  
├── requirements.txt  # Python dependencies  
├── README.md         # Project documentation  
└── resume.jpg        # Image  


![Demo Screenshot](resume.jpg)




