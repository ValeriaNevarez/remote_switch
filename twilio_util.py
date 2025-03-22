from twilio.rest import Client
from secret import account_sid,auth_token
from twilio.twiml.voice_response import Dial, Number, VoiceResponse



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
def Outbound_call(phone_number):
  response = VoiceResponse()
  response.pause(length=10)
  response.play('', digits='w5')
  response.pause(length=60)
  
  print(response)

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

