import sys
import os
import json

sys.path.append(os.path.join(os.getcwd(), "src"))

try:
    from firebase_logger import FirebaseLogger
    logger = FirebaseLogger()
    history = logger.get_history(limit=3)
    
    print("--- LATEST FIREBASE RECORDS ---")
    if history:
        for i, record in enumerate(history):
            print(f"Record {i+1}: Time={record.get('timestamp')}, CPU={record.get('cpu_percent')}%")
    else:
        print("No records found yet. Ensure the server has been running for at least 5 minutes or start it manually to trigger a log.")
except Exception as e:
    print(f"Error: {e}")
