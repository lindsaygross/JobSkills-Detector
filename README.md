sdk: streamlit
app_file: app.py

# 1. Clone and Install

git clone https://github.com/YOUR-USERNAME/skill-detector.git
cd skill-detector
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt


# 2. Create a .env file
HUGGINGFACE_API_KEY=hf_********************************

# 3. Run the CLI
python3 cli_demo.py --text "I have experience in Python, Pandas, and SQL."

# 4. Run the streamlit app
streamlit run app.py
