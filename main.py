from twilio_util import Send_message,Outbound_call,Call_status,Sid_call_logs, Call_list,GetLastCallStatus, GetLastCompletedCallDate
import time 
from database_util import GetListArray
from datetime import date,datetime,timezone

database_list = GetListArray()

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


def ReportRowToString(report_row):
    return  f"""
    <tr>
        <td>{report_row.get("serial_number")}</td>
        <td>{report_row.get("phone_number")}</td>
        <td>{report_row.get("status")}</td>
        <td>{report_row.get("days")}</td>
    </tr>
    """


def ReportRowToString(report_row):
    return  f"""
    <tr>
        <td>{report_row.get("serial_number")}</td>
        <td>{report_row.get("phone_number")}</td>
        <td>{report_row.get("status")}</td>
        <td>{report_row.get("days")}</td>
    </tr>
    """


def GetReportRow(database_row):
    serial_number = database_row.get("serial_number")
    phone_number = database_row.get("phone_number")
    last_call_status = GetLastCallStatus(phone_number)
    status = last_call_status.get("status") if last_call_status is not None else "-"
    last_completed_date = GetLastCompletedCallDate(phone_number)
    days_since = GetDaysSince(last_completed_date) if last_completed_date is not None else None
    days = "-"
    if (days_since == 1):
        days = "Hace "+str(days_since) + " día"
    elif (days_since is not None):
        days = "Hace "+str(days_since) + " días"

    return {"serial_number":serial_number, "phone_number": phone_number, "status": status, "days" : days}

    


def GetReport(database_list):
    report_date = date.today()
    total_devices = len(database_list)
    database_list_range = range(0,len(database_list))
    total_inactive_devices = 0
    total_active_completed_devices = 0
    total_incompleted_call_devices = 0
    inactive_rows = []
    active_rows = []

    for i in database_list_range:
        is_active = database_list[i].get("is_active")

        if (is_active == False ):
            total_inactive_devices += 1
            inactive_rows.append(GetReportRow(database_list[i]))
        else:
            active_phone = database_list[i].get("phone_number")
            last_call_status = GetLastCallStatus(active_phone).get("status")
            if (last_call_status != "completed"):
                total_incompleted_call_devices += 1
                active_rows.append(GetReportRow(database_list[i]))
            else: 
                total_active_completed_devices += 1

    inactive_rows.sort(key=lambda d: d["days"], reverse= True)
    active_rows.sort(key=lambda d: d["days"], reverse= True)    

    inactive_rows_string = ""
    active_rows_string = ""
    for element in inactive_rows:
        inactive_rows_string += ReportRowToString(element)
    for element in active_rows:
        active_rows_string += ReportRowToString(element)

    a = f'''
<html>
<head>
<style>

h1 {{font-family: Helvetica, Arial, sans-serif;
font-weight: normal}}

h2 {{font-family: Helvetica, Arial, sans-serif;
font-weight: normal}}

h3 {{font-family: Helvetica, Arial, sans-serif;
font-weight: normal}}

h4 {{font-family: Helvetica, Arial, sans-serif;
font-weight: normal}}


#actives {{  font-family: Helvetica, Arial, sans-serif;
  border-collapse: collapse;
  width: 40%;}}

#actives td, #actives th {{border: 1px solid #ddd;
  padding: 8px;}}

#actives tr:nth-child(even){{background-color: #f2f2f2;}}

#actives tr:hover {{background-color: #ddd;}}

#actives th {{padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #0270c9;
  color: white;}}

#inactives {{  font-family: Helvetica, Arial, sans-serif;
  border-collapse: collapse;
  width: 40%;}}

#inactives td, #inactives th {{border: 1px solid #ddd;
  padding: 8px;}}

#inactives tr:nth-child(even){{background-color: #f2f2f2;}}

#inactives tr:hover {{background-color: #ddd;}}

#inactives th {{padding-top: 12px;
  padding-bottom: 12px;
  text-align: left;
  background-color: #0270c9;
  color: white;}}


</style>
</head>

<body>

<h1>Reporte semanal</h1>
<h3>Fecha: {report_date}</h3>
<h4>Total de dispositivos: {total_devices}</h4>
<h4>Total de dispositivos activos con llamada completada: {total_active_completed_devices}</h4>
<h4>Total de dispositivos activos con llamada no completada: {total_incompleted_call_devices}</h4>
<h4>Total de dispositivos inactivos: {total_inactive_devices}</h4>


<h2>Tabla de activos</h2>
<table id= "actives">
  <tr>
    <th>No. de serie</th>
    <th>No. de celular</th>
    <th>Estatus</th>
    <th>Último enlace</th>
  </tr>

  {active_rows_string}
</table>

<h2>Tabla de inactivos </h2>
<table id="inactives">
  <tr>
    <th>No. de serie</th>
    <th>No. de celular</th>
    <th>Estatus</th>
    <th>Último enlace</th>
  </tr>

  {inactive_rows_string}
</table>


</body>
</html>
    '''
    return a
  

        
# string = GetReport(database_list)
# print(string)
# f = open("myhtmlfile.html", "w")
# f.write(string)

