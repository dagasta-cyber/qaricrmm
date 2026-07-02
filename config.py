import os
from dotenv import load_dotenv

# Load environmental variables from .env file if it exists
load_dotenv()

PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "127.0.0.1")
DATABASE_PATH = os.getenv("DATABASE_PATH", "qaricrm.db")
SIMULATOR_INTERVAL_SECONDS = int(os.getenv("SIMULATOR_INTERVAL_SECONDS", 40))

# Environment-based credentials. Database settings will take priority over these.
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/gmail/callback")

META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "qari_crm_verify_token")
META_PAGE_ACCESS_TOKEN = os.getenv("META_PAGE_ACCESS_TOKEN", "")
META_WHATSAPP_PHONE_NUMBER_ID = os.getenv("META_WHATSAPP_PHONE_NUMBER_ID", "")
META_WHATSAPP_ACCESS_TOKEN = os.getenv("META_WHATSAPP_ACCESS_TOKEN", "")
