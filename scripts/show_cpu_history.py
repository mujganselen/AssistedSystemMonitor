import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase-key.json")
if not firebase_admin._apps:
    app = firebase_admin.initialize_app(cred)
else:
    app = firebase_admin.get_app()

db = firestore.client()
docs = db.collection("system_stats").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).get()

print("--- HISTORICAL CPU DATA ---")
for d in docs:
    data = d.to_dict()
    timestamp = data.get("timestamp")
    cpu = data.get("cpu_percent")
    if cpu is not None:
        print(f"Time: {timestamp} | CPU: {cpu}%")
