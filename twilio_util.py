from twilio.rest import Client
from secret import account_sid,auth_token
from twilio.twiml.voice_response import Dial, Number, VoiceResponse
from datetime import date,datetime,timezone



client = Client(account_sid, auth_token)

#Función que manda mensaje a un número de celular.
def Send_message(to,text):
  message = client.messages.create(
    from_='+18667487103',
    body= text,
    to= to 
  )
  return message.sid

#Función que acepta un número de teléfono y lo llama. Sostiene la llamada por 70 segundos y retorna el sid de la llamada.
def Outbound_call(phone_number : str, enabled: bool) -> str:
  response = VoiceResponse()
  response.pause(length=10)

  if(enabled == True):
    if(phone_number == "+528713865040"):
      response.play('', digits='w1')
    else:
      response.play('', digits='w5')
  else:
    if(phone_number == "+528713865040"):
      response.play('', digits='w5')
    else:
      response.play('', digits='w1')
  
  response.pause(length=60)

  call = client.calls.create(
    from_= '+18667487103' ,
    to= phone_number,
    twiml=response,
    time_limit= 70
  )
  return call.sid

#Función que acepta un sid de parámetro, y retorna el status de la llamada (busy, completed, not answer, etc)
def Call_status(sid):
  call = client.calls(sid).fetch()
  print(call.status)


#Función en twilio_util que acepta un número de teléfono y retorna un array de todos los Sid de llamada que se le han hecho
def Sid_call_logs(phone_number):
  call = client.calls.list(to= phone_number)
  sid_array = []
  for record in call:
    sid_array.append(record.sid)
  return sid_array 

def Call_list():
  call_list = client.calls.list()
  phone_date_status_array = []
  for record in call_list:
    phone = record.to
    date = record.date_created
    status = record.status
    entry = {"phone": phone, "date": date, "status": status }
    phone_date_status_array.append(entry)
  
  return phone_date_status_array


def GetLastCallStatus(phone_number):
  # return {"status": "completed", "date": datetime.now(timezone.utc)}

  call_list = client.calls.list(limit= 1,to = phone_number)
  if(call_list == []):
    return None

  record = call_list[0]

  status = record.status
  date = record.date_created
  duration = record.duration

  if(status == "completed" and int(duration) < 60):
    status = "incompleted"
  
  return {"status" : status, "date": date}


def GetLastCompletedCallDate(phone_number):
  # return {"status": "completed", "date": datetime.now(timezone.utc)}

  call_list = client.calls.list(to = phone_number, status= "completed")
  if(call_list == []):
    return None
  
  for record in call_list:
    date = record.date_created
    duration = record.duration

    if(int(duration) > 60):
      return date
    
  return None

