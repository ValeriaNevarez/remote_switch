from twilio_util import Send_message,Outbound_call,GetLastCallStatus
import time 
from database_util import GetListArray
from datetime import datetime,timezone

DAYS_BETWEEN_CALLS = 30

database_list = GetListArray()


def GetDaysSince(date: datetime) -> int | None:
    if(date == None):
        return None
    today = datetime.now(timezone.utc)
    diff_days = today - date

    return diff_days.days


def MakeACall(phone_number,enabled):
    print("calling ",phone_number, enabled)
    sid = Outbound_call(phone_number,enabled)
    print(phone_number,sid)
    time.sleep(80)


def ChangeMaster(phone_number):
    print("sending message", phone_number)
    message_to_change_master = '*123456*#+18667487103#'
    Send_message(phone_number, message_to_change_master)


def CallAllNumbers():
    database_list_range = range(0,len(database_list))
    for i in database_list_range:
        phone_number = database_list[i].get("phone_number")
        enabled = database_list[i].get("enabled")
        MakeACall(phone_number,enabled)


def CallAllActiveNumbers():
    database_list_range = range(0,len(database_list))
    for i in database_list_range:
        is_active = database_list[i].get("is_active")
        if(is_active == True):
            active_phone = database_list[i].get("phone_number")
            enabled = database_list[i].get("enabled")
            MakeACall(active_phone,enabled)


def CallNumbersThatNeedIt():
    database_list_range = range(0,len(database_list))
    for i in database_list_range:
        is_active = database_list[i].get("is_active")
        if(is_active == True):
            active_phone = database_list[i].get("phone_number")
            last_call_status = GetLastCallStatus(active_phone)
            status_active_phone = last_call_status.get("status")
            date_active_phone = last_call_status.get("date")
            days_since_call = GetDaysSince(date_active_phone)
            enabled = database_list[i].get("enabled")
            if(status_active_phone == None):
                print("estatus igual a None", active_phone)
                ChangeMaster(active_phone)
                time.sleep(60)  # Wait for the device to process the SMS.
                MakeACall(active_phone,enabled)
            elif(status_active_phone != "completed"):
                print("estatus differente a completed",active_phone, status_active_phone)
                MakeACall(active_phone,enabled)
            elif(days_since_call > DAYS_BETWEEN_CALLS):
                print("dias sin llamada completada excedidos", active_phone)
                MakeACall(active_phone,enabled)


CallNumbersThatNeedIt()
