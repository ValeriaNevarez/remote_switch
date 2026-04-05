import firebase_admin
from firebase_admin import db

from env import load_json_from_base64_env, load_string_from_env


def _load_certificate():
    return firebase_admin.credentials.Certificate(
        load_json_from_base64_env("FIREBASE_SERVICE_ACCOUNT_B64")
    )


cred_obj = _load_certificate()
default_app = firebase_admin.initialize_app(
    cred_obj,
    {"databaseURL": load_string_from_env("FIREBASE_DATABASE_URL")},
)
ref = db.reference("/devices")


def GetListArray():
    return ref.order_by_child("serial_number").get()
