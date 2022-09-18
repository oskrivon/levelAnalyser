from logging import exception
import requests
import threading
import json
import time
import yaml
from yaml.loader import SafeLoader

import market_screener as ms
import tg_msg_preparer as msg_preparer
import tg_msg_sender as msg_sender


def get_updates(offset=0):
    result = requests.get(f'{URL}{TOKEN}/getUpdates?offset={offset}').json()
    return result['result']


def check_message(msg, chat_id):
    global thread_go 

    if msg == '/start':
        users_update(chat_id, users)
    
    if msg == 'stop': 
        thread_go = False
    
    if msg == 'go':
        thread_go = True

    keywords = msg.lower().split()
    if len(keywords) > 1: amount = keywords[1]


def reply_keyboard(chat_id, text):
    reply_markup ={ "keyboard": [["top 10", "top 20"], ["top 30"]], "resize_keyboard": True, "one_time_keyboard": True}
    data = {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}
    requests.post(f'{URL}{TOKEN}/sendMessage', data=data)


def run():
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


def user_saver():
    file = open('users', 'w+')
    user = [158, 98752]
    yaml.dump(user, file, sort_keys=False, default_flow_style=False)
    file.close()


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


def annunciator(screening_type, header, delay):
    while thread_go:
        # tre=y reading user ids
        try:
            with open('users.yaml') as f: users = yaml.load(f, Loader=SafeLoader)
            f.close()
        except Exception as e:
            print('>>> users file error:', e)     

        screening = screening_type(num=10)
        print(screening)
        msg = msg_preparer.msg_formatter(screening, header)
        print(msg)

        for user in users:            
            sender.send_message(user, msg)
            sender.telegram_send_media_group('images', user)
        
        time.sleep(delay)


if __name__ == '__main__':
    path = 'screener_token.txt'
    TOKEN = open(path, 'r').read()
    URL = 'https://api.telegram.org/bot'

    screener = ms.Screener()
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

    thread_go = True
    th_ping = threading.Thread(target=annunciator, 
                               args=(screener.get_screening, header_volumes, 1))
    th_ping.daemon = True
    th_ping.start()

    th_natrs = threading.Thread(target=annunciator, 
                                args=(screener.get_top_natr, header_natrs, 1))
    th_natrs.daemon = True
    th_natrs.start()

    th_funding = threading.Thread(target=annunciator, 
                                  args=(screener.get_upcoming_fundings, header_funding, 1))
    th_funding.daemon = True
    th_funding.start()

    print('>>> alerts launched')
    run()