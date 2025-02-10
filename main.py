from twilio_util import Send_message,Outbound_call,Call_status,Sid_call_logs
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
'+528715775427',
'+528711226991',
'+528717812721',
'+528712331536',
'+528717812697',
'+528712311936',
'+528711201654',
'+528713952058',
'+528712315092',
'+528713956413',
'+528711209395',
'+528712321992',
'+528713865040',
'+528713971807',
'+528713460690']

# +528711213668 lo quito cristian y lo cambio por el +528715775427
# +528711226763 lo quito cristian y lo cambio por el +528717812721
    
# new_phone_list = ['+528711226991', 
# '+528712315092']

# for phone_number in new_phone_list:
#     sid = Send_message(phone_number,message_to_change_master)
#     print(phone_number,sid)

for phone_number in phone_list:
    sid = Outbound_call(phone_number)
    print(phone_number,sid)
    time.sleep(80)

# Call_status('CA1041dd66e60d823d35a05b882829ef13')

# for phone_number in phone_list:
#     sid_logs = Sid_call_logs(phone_number)
#     for phone_number in sid_logs:
#         Call_status(phone_number)

# print(Send_message('+528711226965',message_to_change_master))
# time.sleep(60)
# print(Outbound_call('+528711213003'))
