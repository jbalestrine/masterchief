@echo off
REM Activate virtual environment if present
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)
echo Starting TF Wizard (FastAPI) on http://127.0.0.1:8000
python -m uvicorn tf_wizard.app:app --reload
