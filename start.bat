@echo off
REM MasterChief Platform Startup Script for Windows

echo ======================================
echo Starting MasterChief Platform
echo ======================================

REM Check if Docker is available
where docker >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Docker detected. Starting with Docker Compose...
    docker-compose up -d
    
    echo.
    echo ======================================
    echo Platform started!
    echo ======================================
    echo.
    echo Access the platform at:
    echo   API: https://localhost:8443
    echo   Grafana: http://localhost:3000
    echo   Prometheus: http://localhost:9090
    echo.
    echo View logs with: docker-compose logs -f
    echo Stop with: docker-compose down
) else (
    echo Starting platform directly...
    
    REM Check if Python is available
    where python >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Python is required but not found.
        exit /b 1
    )
    
    REM Install dependencies if needed
    python -c "import flask" 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Installing dependencies...
        pip install -r requirements.txt
    )
    
    REM Start the platform
    python platform\main.py
)
