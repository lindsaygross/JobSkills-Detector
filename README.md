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
```bash
git clone https://github.com/lindsaygross/JobSkills-Detector.git
cd JobSkills-Detector
```

2. **Set up the Environment**  
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\activate
pip install --upgrade pip
```

3. **Install Requirements**  
```bash
pip install -r requirements.txt
```

4. **Run Streamlit**  
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Open http://localhost:8501 (or replace `localhost` with your LAN IP if opening from another device). If the port is already taken, provide a different number with `--server.port` (e.g., `--server.port 8502`). Need to reclaim a busy port? Run `lsof -i :8501` (macOS/Linux) to find and stop the blocking process.

### Using the Streamlit UI
1. Upload a PDF/TXT resume, paste raw text, or toggle the **“Use sample resume”** checkbox in the sidebar.
2. Enter a job title or keyword in **Job search** and optionally add a preferred location (e.g., “Remote”, “New York”).
3. Tune the number of jobs to fetch and the skill-threshold slider, then wait a few seconds for the analysis to complete.
4. Review the tabs:
   - **Job explorer** (default) shows the filtered Remotive postings with card/table views and CSV export.
   - **Skill gaps** visualizes missing skills and lets you download the gap table.
   - **Resume signals** ranks the most-evident skills detected in your resume.
5. Expand “Peek at the processed resume text” at the bottom if you need to debug extraction issues.

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

