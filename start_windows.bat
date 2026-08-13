@echo off
python -m pip install -r requirements.txt
python seed_data.py
python -m streamlit run app.py
pause
