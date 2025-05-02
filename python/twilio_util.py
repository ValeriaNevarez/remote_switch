from twilio.rest import Client
from secret import account_sid,auth_token
from twilio.twiml.voice_response import VoiceResponse

client = Client(account_sid, auth_token)

# Prototype devices have inverted polarity.
INVERTED_PHONE_NUMBERS = ['+528713293364','+528713971819','+528713971823', '+528713865040', '+528713971807', '+528713460690']


def Send_message(to,text):
  message = client.messages.create(
    from_='+18667487103',
    body= text,
    to= to 
  )
  return message.sid


def Outbound_call(phone_number : str, enabled: bool) -> str:
  response = VoiceResponse()
  response.pause(length=10)

  if(enabled == True):
    if(phone_number in INVERTED_PHONE_NUMBERS):
      response.play('', digits='w1')
    else:
      response.play('', digits='w5')
  else:
    if(phone_number in INVERTED_PHONE_NUMBERS):
      response.play('', digits='w5')
    else:
      response.play('', digits='w1')
  
  response.pause(length=60)
  print(response)

  call = client.calls.create(
    from_= '+18667487103' ,
    to= phone_number,
    twiml=response,
    time_limit= 70
  )
  return call.sid


def Call_status(sid):
  call = client.calls(sid).fetch()
  print(call.status)


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
  call_list = client.calls.list(to = phone_number, status= "completed")
  if(call_list == []):
    return None
  
  for record in call_list:
    date = record.date_created
    duration = record.duration

    if(int(duration) > 60):
      return date
    
  return None
