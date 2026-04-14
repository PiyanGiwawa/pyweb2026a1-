import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

doc = {
  "name": "石詠澤",
  "mail": "s1131242@0365st.pu.edu.tw",
  "lab": 579
}

doc_ref = db.collection("靜宜資管2026a").document("piyan")
doc_ref.set(doc)