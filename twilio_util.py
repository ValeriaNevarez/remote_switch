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
