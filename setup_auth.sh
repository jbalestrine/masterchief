#!/bin/bash
# MasterChief Authentication Setup Script
# This script helps set up authentication and integrations

echo "🔧 MasterChief Authentication Setup"
echo "=================================="

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment is active: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Please activate your venv first:"
    echo "   source venv/Scripts/activate  # Windows"
    echo "   source venv/bin/activate     # Linux/Mac"
    exit 1
fi

echo ""
echo "📦 Installing new dependencies..."

pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🔧 Setting up environment configuration..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo ""
    echo "📝 Please edit .env file with your credentials:"
    echo "   - Azure AD app registration details"
    echo "   - OKTA application credentials"
    echo "   - GitHub OAuth app credentials"
    echo ""
    echo "💡 Setup Instructions:"
    echo "   1. Azure AD: https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app"
    echo "   2. OKTA: https://developer.okta.com/docs/guides/implement-oauth-for-okta/main/"
    echo "   3. GitHub: https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps"
else
    echo "ℹ️  .env file already exists"
fi

echo ""
echo "🚀 Setup complete! Run the application with:"
echo "   python main.py"
echo ""
echo "🌐 Access the web interface at: http://localhost:8080"
echo "🔐 Login options will be available based on your .env configuration"