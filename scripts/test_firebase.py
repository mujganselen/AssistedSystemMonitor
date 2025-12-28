import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.firebase_logger import FirebaseLogger
import time

logger = FirebaseLogger()

print("Triggering manual log...")
logger.log_stats()

print("Waiting a moment for Firestore to settle...")
time.sleep(2)

print("Retrieving history...")
history = logger.get_history(limit=5)

if history:
    print(f"Successfully retrieved {len(history)} records.")
    for record in history:
        print(f"- {record['timestamp']}: CPU {record['cpu_percent']}%")
else:
    print("No records found. Check if Firestore is in 'Test Mode' and the collection is created.")
