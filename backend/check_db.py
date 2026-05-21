import firebase_admin
from firebase_admin import credentials, firestore, db
import json
import sys

def main():
    print("Starting script...")
    sys.stdout.flush()
    try:
        cred = credentials.Certificate("firebase-key.json")
        print("Credentials loaded.")
        sys.stdout.flush()
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return

    try:
        with open("firebase-key.json", "r") as f:
            key_data = json.load(f)
        project_id = key_data.get("project_id", "hazir-57557")
        print(f"Project ID: {project_id}")
        sys.stdout.flush()
    except Exception as e:
        print(f"Error reading project ID: {e}")
        project_id = "hazir-57557"

    try:
        firebase_admin.initialize_app(cred, {
            'databaseURL': f'https://{project_id}-default-rtdb.firebaseio.com/'
        })
        print("Firebase app initialized.")
        sys.stdout.flush()
    except ValueError:
        print("Firebase app already initialized.")
        sys.stdout.flush()

    print("\n" + "="*50)
    print(" FIREBASE DATABASE EXTRACTION REPORT ".center(50, "="))
    print("="*50 + "\n")
    sys.stdout.flush()

    try:
        print("Connecting to Firestore...")
        sys.stdout.flush()
        db_client = firestore.client()
        collections = db_client.collections()
        print("Got collections generator.")
        sys.stdout.flush()
        
        has_firestore_data = False
        for collection in collections:
            has_firestore_data = True
            print(f"\nCollection: '{collection.id}'")
            sys.stdout.flush()
            docs = collection.stream()
            count = 0
            for doc in docs:
                count += 1
                print(f"  Document [{doc.id}]:")
                data = doc.to_dict()
                for k, v in data.items():
                    print(f"    - {k}: {v}")
            print(f"  Total {collection.id}: {count}")
            sys.stdout.flush()
            
        if not has_firestore_data:
            print("  Firestore is empty or has no collections.")
            sys.stdout.flush()
    except Exception as e:
        print(f"Error reading Firestore: {e}")
        has_firestore_data = False
        sys.stdout.flush()

    try:
        print("\nConnecting to Realtime Database...")
        sys.stdout.flush()
        ref = db.reference('/')
        data = ref.get()
        if not data:
            print("  Realtime Database is empty.")
        else:
            for node_name, node_data in data.items():
                print(f"\nNode: '{node_name}'")
                if isinstance(node_data, dict):
                    print(f"  Total items: {len(node_data)}")
                    for k, v in node_data.items():
                        print(f"  [{k}]:")
                        if isinstance(v, dict):
                            for sub_k, sub_v in v.items():
                                print(f"    - {sub_k}: {sub_v}")
                        else:
                            print(f"    - {v}")
                else:
                    print(f"  Value: {node_data}")
        sys.stdout.flush()
    except Exception as e:
        print(f"  Could not read Realtime Database: {e}")
        sys.stdout.flush()

    print("\n" + "="*50)
    print(" END OF REPORT ".center(50, "="))
    print("="*50 + "\n")
    sys.stdout.flush()

if __name__ == "__main__":
    main()
