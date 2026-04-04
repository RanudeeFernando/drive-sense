from cloud_server.cloud.firestore_database import FirestoreDatabase

db = FirestoreDatabase().get_client()

db.collection("test_connection").document("ping").set({
    "status": "connected"
})

doc = db.collection("test_connection").document("ping").get()
print(doc.to_dict())