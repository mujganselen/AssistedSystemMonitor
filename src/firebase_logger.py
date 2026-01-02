import firebase_admin
from firebase_admin import credentials, firestore
import psutil
from datetime import datetime
import threading
import time
import os

class FirebaseLogger:
    def __init__(self, key_path="firebase-key.json"):
        self.db = None
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(key_path)
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            print("Firebase initialized successfully.")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")

    def log_stats(self):
        """Logs current system stats to Firestore."""
        if not self.db:
            return

        try:
            stats = {
                "timestamp": firestore.SERVER_TIMESTAMP,
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage(os.path.abspath(os.sep)).percent
            }
            self.db.collection("system_stats").add(stats)
            print(f"Stats logged to Firebase at {datetime.now()}")
        except Exception as e:
            print(f"Error logging to Firebase: {e}")

    def get_history(self, limit=10):
        """Retrieves historical stats from Firestore."""
        if not self.db:
            return []

        try:
            docs = self.db.collection("system_stats")\
                .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                .limit(limit)\
                .get()
            
            history = []
            for doc in docs:
                data = doc.to_dict()
                if "timestamp" in data and data["timestamp"]:
                    data["timestamp"] = data["timestamp"].isoformat()
                history.append(data)
            return history
        except Exception as e:
            print(f"Error retrieving history: {e}")
            return []

def start_background_logging(logger, interval=60):
    """Starts a background thread that logs stats periodically."""
    def run():
        while True:
            logger.log_stats()
            time.sleep(interval)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread
