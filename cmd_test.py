from sys import argv
from pybit import inverse_perpetual

import telegram_posting as bot


TOKEN = open('telegram_key.txt', 'r').read()

quotation = argv[1]

#quotation = 'BTCUSDT'

session_unauth = inverse_perpetual.HTTP(
    endpoint="https://api.bybit.com"
)

print(quotation)

f = open(quotation + '.txt', 'w')

i = 0
while i < 10:
    data = session_unauth.latest_information_for_symbol(symbol=quotation)
    current_price = float(data['result'][0]['last_price'])

    f.write(str(current_price) + '\n')
    #msg = quotation + str(current_price)
    #bot.telegram_message_send(msg, TOKEN)
    print(quotation, current_price)
    i +=1

f.close()