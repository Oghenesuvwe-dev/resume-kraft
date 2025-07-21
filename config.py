import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application settings
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

# Storage settings
STORAGE_PATH = os.getenv("STORAGE_PATH", "storage")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
RESUME_FOLDER = os.getenv("RESUME_FOLDER", "resumes")

# PDF conversion settings
PDF_CONVERSION_ENABLED = os.getenv("PDF_CONVERSION_ENABLED", "False").lower() == "true"

# Create directories if they don't exist
os.makedirs(STORAGE_PATH, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESUME_FOLDER, exist_ok=True)