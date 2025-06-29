import os
from dotenv import load_dotenv

load_dotenv()

# Google Calendar API Configuration
SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

# Google AI Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8001
OAUTH_PORT = 8000

# CORS Configuration
CORS_ORIGINS = ["*"]  # In production, specify your frontend URL
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]