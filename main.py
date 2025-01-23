from twilio_util import Send_message,Outbound_call
import time 


test_phone = '+16508611877'
message_to_change_master = '*123456*#+18667487103#'
phone_list = ['+528711213669',
'+528711222383',
'+528711203824',
'+528711226965',
'+528711213670',
'+528711212584',
'+528712321789',
'+528713993607',
'+528711213668',
'+528711226991',
'+528711226763',
'+528712331536',
'+528711213003',
'+528712311936',
'+528711201654',
'+528713952058',
'+528712315092',
'+528713956413',
'+528711209395',
'+528712321992']

# for phone_number in phone_list:
#     sid = Send_message(phone_number,message_to_change_master)
#     print(phone_number,sid)

for phone_number in phone_list:
    sid = Outbound_call(phone_number)
    print(phone_number,sid)
    time.sleep(80)

