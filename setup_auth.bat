@echo off
REM MasterChief Authentication Setup Script (Windows)
REM This script helps set up authentication and integrations

echo 🔧 MasterChief Authentication Setup
echo ==================================

REM Check if virtual environment is active
if defined VIRTUAL_ENV (
    echo ✅ Virtual environment is active: %VIRTUAL_ENV%
) else (
    echo ⚠️  No virtual environment detected. Please activate your venv first:
    echo    venv\Scripts\activate
    pause
    exit /b 1
)

echo.
echo 📦 Installing new dependencies...

pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo 🔧 Setting up environment configuration...

if not exist .env (
    copy .env.example .env
    echo ✅ Created .env file from template
    echo.
    echo 📝 Please edit .env file with your credentials:
    echo    - Azure AD app registration details
    echo    - OKTA application credentials
    echo    - GitHub OAuth app credentials
    echo.
    echo 💡 Setup Instructions:
    echo    1. Azure AD: https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app
    echo    2. OKTA: https://developer.okta.com/docs/guides/implement-oauth-for-okta/main/
    echo    3. GitHub: https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps
) else (
    echo ℹ️  .env file already exists
)

echo.
echo 🚀 Setup complete! Run the application with:
echo    python main.py
echo.
echo 🌐 Access the web interface at: http://localhost:8080
echo 🔐 Login options will be available based on your .env configuration

pause