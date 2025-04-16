import firebase_admin
from firebase_admin import db
import os


dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'firebase_private_key.json')

cred_obj = firebase_admin.credentials.Certificate(filename)
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL':' https://remote-switch-14373-default-rtdb.firebaseio.com/'
    })
ref = db.reference("/devices")

def GetListArray():
    list_array = ref.order_by_child("serial_number").get() #Firebase data in an array
    return list_array



