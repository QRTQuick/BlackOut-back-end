import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
TEMP_EXPIRY_SECONDS = 600  # 10 minutes