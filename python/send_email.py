#
# Followed these tutorials:
# - https://mailtrap.io/blog/send-emails-with-gmail-api/
# - https://developers.google.com/workspace/gmail/api/guides/sending?hl=es-419#python
#

import base64
import os.path
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage
from datetime import date,datetime,timezone
from twilio_util import GetLastCallStatus, GetLastCompletedCallDate
from database_util import GetListArray

USER_EMAIL = "santiagomendoza@gmail.com"

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


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
        <td>{report_row.get("client_name")}</td>
        <td>{report_row.get("client_number")}</td>
        <td>{report_row.get("status")}</td>
        <td>{report_row.get("days")}</td>
    </tr>
    """


def GetReportRow(database_row):
    client_name = database_row.get("client_name")
    client_number = database_row.get("client_number")
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

    return {"serial_number":serial_number, "client_name": client_name, "client_number": client_number, "phone_number": phone_number, "status": status, "days" : days}


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
  border-collapse: collapse;}}

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
  border-collapse: collapse;}}

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
    <th>Cliente</th>
    <th>No. de cliente</th>
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
    <th>Cliente</th>
    <th>No. de cliente</th>
    <th>Estatus</th>
    <th>Último enlace</th>
  </tr>

  {inactive_rows_string}
</table>


</body>
</html>
    '''
    return a


def SendEmail(body: str, to: str):

  dirname = os.path.dirname(__file__)
  token_filename = os.path.join(dirname, 'token.json')
  secrets_filename = os.path.join(dirname, 'springwater_oauth.json')


  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(token_filename):
    creds = Credentials.from_authorized_user_file(token_filename, SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          secrets_filename, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token_filename, "w") as token:
      token.write(creds.to_json())

  try:
    service = build("gmail", "v1", credentials=creds)

    message = EmailMessage()

    message["To"] = to
    message["From"] = "springwater.switchremoto@gmail.com"
    message["Subject"] = "Reporte semanal switch remoto"
    message["Cc"] = "info@springwater.com.mx, pepemanboy@gmail.com"
    message.set_content(body, subtype='html')

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"raw": encoded_message}
    # pylint: disable=E1101
    send_message = (
        service.users()
        .messages()
        .send(userId="me", body=create_message)
        .execute()
    )
    print(f'Message Id: {send_message["id"]}')
  except HttpError as error:
    print(f"An error occurred: {error}")


database_list = GetListArray()
SendEmail(GetReport(database_list),USER_EMAIL)
