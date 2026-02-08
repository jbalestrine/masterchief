#!/usr/bin/env bash
if [ -f .venv/bin/activate ]; then
  . .venv/bin/activate
fi
echo "Starting TF Wizard (FastAPI) on http://127.0.0.1:8000"
python -m uvicorn tf_wizard.app:app --reload
