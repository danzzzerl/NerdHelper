import pyrebase

firebaseConfig = { 'apiKey': "AIzaSyAgr3Z6G2U_fHwGUfuiPwMRsphglgvLVZM",
  'authDomain': "nerdhelper-d8a69.firebaseapp.com",
  'databaseURL': "https://nerdhelper-d8a69-default-rtdb.asia-southeast1.firebasedatabase.app",
  'projectId':"nerdhelper-d8a69",
  'storageBucket': "nerdhelper-d8a69.appspot.com",
  'messagingSenderId': "863254242724",
  'appId': "1:863254242724:web:2ef22eefbd6513475e0d31",
  'measurementId': "G-PG3HGXZY26"}

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()





