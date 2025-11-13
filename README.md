# JobSkills Detector

Final project for **Duke AIPI-503 Python Bootcamp**.  
The goal of the project is to detect technical skills from resumes or job text using Python.  

---

## Features
- Upload a **PDF/TXT resume** or **paste raw text**, or explore using the built-in sample resume.
- Pull live postings from the free **Remotive jobs API** with an optional preferred-location filter.
- Visualize gaps between resume skills and job demand with Altair charts and CSV downloads.
- Explore ranked **resume skill signals**, inspect the processed resume text, and export job data.
- Use either the **Streamlit web app** or the **CLI** for quick experimentation.  

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
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

Open http://localhost:8501 (or replace `localhost` with your LAN IP if opening from another device). If the port is already taken, provide a different number with `--server.port`.

---

## How to Run the CLI Version

Detect top resume skills directly from text:

```
python cli_demo.py --mode skills --text "I have Python, Pandas and AWS experience." --top-k 10
```

Analyze resume gaps vs. live jobs:

```
python cli_demo.py --mode gap \
  --resume "path/to/resume.pdf" \
  --job-query "data scientist" \
  --num-jobs 8 \
  --top-k 10
```

Manual text input works in either mode by providing `--text "..."` instead of `--resume`.

# Python Version

This project was built and tested with:

Python 3.9+

## Hugging Face Space
Click to use JobSkills detector app:
https://huggingface.co/spaces/Lindsaygross/jobskills

# Project Structure

├── app.py            # Streamlit app  
├── api.py            # API logic  
├── cli_demo.py       # CLI demo runner  
├── requirements.txt  # Python dependencies  
├── README.md         # Project documentation  
└── resume.jpg        # Image  


![Demo Screenshot](resume.jpg)



