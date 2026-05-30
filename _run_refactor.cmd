@echo off
cd /d C:\Users\Echo\masterchief
C:\Users\Echo\masterchief\venv\Scripts\python.exe _refactor.py > _refactor_out.txt 2>&1
echo EXIT_CODE=%ERRORLEVEL%
type _refactor_out.txt
