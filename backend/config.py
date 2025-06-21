import os
import base64
import firebase_admin
from firebase_admin import credentials, firestore, auth
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FIREBASE_CREDENTIALS_PATH = "firebase-credentials.json"

def initialize_firebase():
    try:
        # Decode Base64 env var if file is missing
        if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
            firebase_b64 = os.getenv("FIREBASE_CREDENTIALS_B64")
            if not firebase_b64:
                raise RuntimeError("FIREBASE_CREDENTIALS_B64 environment variable not set")
            
            logger.info("Decoding Firebase credentials from environment variable")
            with open(FIREBASE_CREDENTIALS_PATH, "wb") as f:
                f.write(base64.b64decode(firebase_b64))

        # Initialize Firebase app only once
        if not firebase_admin._apps:
            logger.info("Initializing Firebase app")
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        raise

# Initialize Firebase when module is imported
initialize_firebase()

def get_db():
    try:
        return firestore.client()
    except Exception as e:
        logger.error(f"Failed to get Firestore client: {str(e)}")
        raise

def get_auth():
    return auth