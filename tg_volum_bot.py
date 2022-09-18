import os
from datetime import datetime
import requests
import threading
import json
import time
import yaml
from yaml.loader import SafeLoader

import market_screener as ms


def get_updates(offset=0):
    result = requests.get(f'{URL}{TOKEN}/getUpdates?offset={offset}').json()
    return result['result']


def send_message(chat_id, text):
    requests.get(f'{URL}{TOKEN}/sendMessage?chat_id={chat_id}&text={text}')


def send_photo(chat_id, img):
    files = {'photo': open(img, 'rb')}
    requests.post(f'{URL}{TOKEN}/sendPhoto?chat_id={chat_id}', files=files)


def telegram_send_media_group(path, token, chat_id):    
    url = "https://api.telegram.org/bot" + token + "/sendMediaGroup"
    channel_id = "@level_signals"

    files = dict.fromkeys(os.listdir(path))
    folder = path + '/'

    media_list = []

    for key in files:
        files[key] = open(folder + key, 'rb')

        media_data = dict.fromkeys(['type', 'media', 'caption'])
        media_data['type'] = 'photo'
        media_data['media'] = 'attach://' + key
        media_data['caption'] = key
        
        media_list.append(media_data)

    media = json.dumps(media_list)

    params = {
            'chat_id': chat_id, 
            'media': media
            }

    r = requests.post(url, params= params, files= files)


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


def send_quotes(chat_id, dictionary, amount):
    counter = 0
    msg = ''
    for i in dictionary:
        msg += i + ': $' + str(dictionary[i]) + '\n'
        #send_message(chat_id, i + ': $' + str(dictionary[i]))
        counter += 1
        if counter >= amount: break

    send_message(chat_id, msg)


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

def msg_formatter(screening):
    msg = 'quotation: 24h vol | oi | funding time | natr' + '\n'
    for i in screening:
        quot = i[0]
        volume = num_formatter(i[1])
        oi = num_formatter(i[2])
        funding_time = i[3]
        natr = round(float(i[4]), 2)

        msg += quot + ': $' + str(volume) + ' | ' + str(oi) + ' | ' + \
               str(funding_time) + ' | ' + str(natr) + '\n'
    return msg


def num_formatter(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'),
                         ['', 'K', 'M', 'B', 'T'][magnitude])


def date_formatter(date_time_str):
    date = datetime.fromisoformat(date_time_str[:-1])
    return date.strftime('%m-%d %H:%M:%S')


def annunciator():
    while thread_go:
        # reading user ids
        with open('users.yaml') as f: users = yaml.load(f, Loader=SafeLoader)
        f.close()

        screening = screener.get_screening(num=10)
        print(screening)
        msg = msg_formatter(screening)
        print(msg)

        for user in users:            
            send_message(user, msg)
            telegram_send_media_group('images', TOKEN, user)
        
        time.sleep(60)


if __name__ == '__main__':
    TOKEN = open('screener_token.txt', 'r').read()
    URL = 'https://api.telegram.org/bot'

    screener = ms.Screener()

    # creating file with users id (if not exist)
    file = open('users.yaml', 'a')
    file.close()

    users = []
    with open('users.yaml') as f:
        users = yaml.load(f, Loader=SafeLoader)
        print(users)
    f.close()

    thread_go = True
    th_ping = threading.Thread(target=annunciator)
    th_ping.daemon = True
    th_ping.start()

    print('>>>> alerts launched')
    run()