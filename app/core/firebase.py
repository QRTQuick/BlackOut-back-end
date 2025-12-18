import firebase_admin
from firebase_admin import credentials, db
from app.core.config import FIREBASE_DB_URL
import os

# Initialize Firebase only if the key file exists
firebase_initialized = False

if os.path.exists("firebase_key.json"):
    try:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})
        firebase_initialized = True
    except Exception as e:
        print(f"Firebase initialization failed: {e}")
        firebase_initialized = False
else:
    print("Warning: firebase_key.json not found. Firebase features disabled.")
    firebase_initialized = False

def update_job(task_id: str, data: dict):
    if firebase_initialized:
        try:
            ref = db.reference(f"jobs/{task_id}")
            ref.update(data)
        except Exception as e:
            print(f"Firebase update failed: {e}")
    else:
        print(f"Firebase disabled - would update job {task_id}: {data}")