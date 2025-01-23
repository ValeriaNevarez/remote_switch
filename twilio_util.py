from twilio.rest import Client
from secret import account_sid,auth_token


client = Client(account_sid, auth_token)

def Send_message(to,text):
  message = client.messages.create(
    from_='+18667487103',
    body= text,
    to= to 
  )
  return message.sid

def Outbound_call(phone_number):
  call = client.calls.create(
    from_= '+18667487103' ,
    to= phone_number,
    url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient",
    time_limit= 70
  )
  return call.sid

