from logging import exception
import requests
import threading
import multiprocessing
import json
import time
import datetime
import yaml
from yaml.loader import SafeLoader

import market_screener as ms
import tg_msg_preparer as msg_preparer
import tg_msg_sender as msg_sender
import tg_img_table_creator as img_creator


def get_updates(offset=0):
    result = requests.get(f'{URL}{TOKEN}/getUpdates?offset={offset}').json()
    return result['result']


def check_message(msg, chat_id):
    global thread_go 

    if msg == '/start':
        users_update(chat_id, users)
    
    if msg == 'help':
        msg = ('"volumes" to get the top 10 quotes with the best volumes at the moment' + '\n'+
                '"NATRs" to get the top 10 quotes with the best NATR' + '\n' +
                '"fundings" to get the top quotes with the best fundings rate')
        sender.send_message(chat_id, msg)
    
    if msg == 'stop': 
        thread_go = False
    
    if msg == 'go':
        thread_go = True

    if msg == 'volumes':
        sender.send_message(chat_id, 'top 10 qoutes by volume')
        sender.send_photo(chat_id, 'screener_results/' + 'get_screening' + '.png')
        #sender.send_message(chat_id, msg_volumes) 
    
    if msg == 'NATRes':
        sender.send_message(chat_id, 'top 10 qoutes by NATR')
        sender.send_photo(chat_id, 'screener_results/' + 'get_top_natr' + '.png')
        #sender.send_message(chat_id, msg_natrs) 

    if msg == 'fundings':
        sender.send_message(chat_id, 'top qoutes by funding rate')
        sender.send_photo(chat_id, 'screener_results/' + 'get_upcoming_fundings' + '.png')
        #sender.send_message(chat_id, msg_fundings) 

    keywords = msg.lower().split()
    if len(keywords) > 1: amount = keywords[1]
    
    reply_keyboard(chat_id)


def reply_keyboard(chat_id, text='select metric'):
    reply_markup ={ "keyboard": [['volumes', 'NATRes', 'fundings'], ['help']], "resize_keyboard": True, "one_time_keyboard": True}
    data = {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}
    requests.post(f'{URL}{TOKEN}/sendMessage', data=data)


def receiving_messages():
    update_id = get_updates()[-1]['update_id'] # Присваиваем ID последнего отправленного сообщения боту
    while True:
        #time.sleep(10)
        messages = get_updates(update_id) # Получаем обновления
        for message in messages:
            # Если в обновлении есть ID больше чем ID последнего сообщения, значит пришло новое сообщение
            if update_id < message['update_id']:
                chat_id = message['message']['chat']['id']
                msg = message['message']['text']

                #reply_keyboard(chat_id, 'select top')

                update_id = message['update_id'] # Присваиваем ID последнего отправленного сообщения боту
                print(f"ID пользователя: {chat_id}, Сообщение: {msg}")

                check_message(msg, chat_id)


def users_update(chat_id, users):
    #file = open('users.yaml', 'a+')
    if chat_id in users:
        print('user are exist')
    else:
        file = open('users.yaml', 'a+')
        users.append(chat_id)
        user = []
        user.append(chat_id)
        yaml.dump(user, file, sort_keys=False, default_flow_style=False)
        file.close()

        with open('users.yaml') as f:
            users = yaml.load(f, Loader=SafeLoader)
            print(users)
        f.close()


def annunciator(screening_type, header, delay, funding_flag='non'):
    while thread_go:
        # try reading user ids
        try:
            with open('users.yaml') as f: users = yaml.load(f, Loader=SafeLoader)
            f.close()
        except Exception as e:
            print('>>> users file error:', e)

        msg_flag = True

        screening = screening_type(num=10)
        msg = msg_preparer.msg_formatter(screening, header, funding_flag)
        df_formated = msg_preparer.df_formatter(screening[0])
        img_creator.img_table_creator(df_formated, funding_flag)

        print(msg)

        if funding_flag == 'get_screening':
            msg_volumes = msg
        
        if funding_flag == 'get_top_natr':
            msg_natrs = msg

        if funding_flag == 'get_upcoming_fundings':
            msg_fundings = msg
            
            fundings_hours = [2, 10, 18]
            flag_break_hours = [3, 11, 19]
            calculating_minuts = 54
            now = datetime.datetime.now()
            
            if now.hour in fundings_hours and now.minute > calculating_minuts and msg_flag == True:
                print('now')
                msg_flag = False

                for user in users:            
                    sender.send_message(user, msg)
                    sender.send_photo(user, 'screener_results/' + funding_flag + '.png')
                    sender.telegram_send_media_group(user, 'images')
            
            if now.hour in flag_break_hours:
                msg_flag = True
            
        time.sleep(delay)


if __name__ == '__main__':
    path = 'screener_token.txt'
    TOKEN = open(path, 'r').read()
    URL = 'https://api.telegram.org/bot'

    screener = ms.Screener('binance')
    sender = msg_sender.TgSender(TOKEN, URL)

    # creating file with users id (if not exist)
    file = open('users.yaml', 'a')
    file.close()

    users = []
    with open('users.yaml') as f:
        users = yaml.load(f, Loader=SafeLoader)
        print(users)
    f.close()

    header_volumes = 'top 10 qoutes by volume'
    header_natrs = 'top 10 qoutes by natr'
    header_funding = 'top 10 qoutes by upcoming funding'

    msg_volumes = '1122'
    msg_natrs = '1125'
    msg_fundings = '1233'

    thread_go = True
    th_ping = threading.Thread(target=annunciator, 
                               args=(screener.get_screening, 
                                     header_volumes, 1, 'get_screening'))
    th_ping.daemon = True
    th_ping.start()

    th_natrs = threading.Thread(target=annunciator, 
                                args=(screener.get_top_natr, 
                                      header_natrs, 1, 'get_top_natr'))
    th_natrs.daemon = True
    th_natrs.start()

    th_funding = threading.Thread(target=annunciator, 
                                  args=(screener.get_upcoming_fundings, 
                                        header_funding, 60, 'get_upcoming_fundings'))
    th_funding.daemon = True
    th_funding.start()

    print('>>> alerts launched')
    receiving_messages()