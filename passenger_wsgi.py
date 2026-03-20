import sys
import os

# Add your app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables if .env exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from main import app as application
