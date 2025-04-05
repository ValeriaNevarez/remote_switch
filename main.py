from twilio_util import Send_message,Outbound_call,Call_status,Sid_call_logs, Call_list,GetLastCallStatus
import time 
from database_util import GetListArray
from datetime import date,datetime,timezone

database_list = GetListArray()

def MakeACall(phone_number,enabled):
    print("calling ",phone_number, enabled)
    # sid = Outbound_call(phone_number,enabled)
    # print(phone_number,sid)
    # time.sleep(80)

def ChangeMaster(phone_number):
    print("sending message", phone_number)
    # message_to_change_master = '*123456*#+18667487103#'
    # Send_message(phone_number, message_to_change_master)

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
            checkpoint = False
            if(status_active_phone != "completed"):
                print("estatus differente a completed",active_phone, status_active_phone)
                MakeACall(active_phone,enabled)
                checkpoint = True
            if(status_active_phone == None):
                print("estatus igual a None", active_phone)
                ChangeMaster(active_phone)
                MakeACall(active_phone,enabled)
            if(checkpoint == False and days_since_call > 20):
                print("dias sin llamada completada mayor a 20", active_phone)
                MakeACall(active_phone,enabled)


def GetDaysSince(date: datetime) -> int | None:
    if(date == None):
        return None
    today = datetime.now(timezone.utc)
    diff_days = today - date

    return diff_days.days


CallNumbersThatNeedIt()


    




