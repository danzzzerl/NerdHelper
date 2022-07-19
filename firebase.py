import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databasURL': 'https://nerdhelper-d8a69-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

ref = db.reference('/')
ref.set()