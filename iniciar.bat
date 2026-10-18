@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
pip install -q -r requirements.txt --disable-pip-version-check
python app.py
pause