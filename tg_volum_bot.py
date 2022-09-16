from ast import keyword
import os
import requests
import json
import time
import yaml
from yaml.loader import SafeLoader

import analyzer


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
    if msg == '/start':
        users_update(chat_id, users)

    keywords = msg.lower().split()
    if len(keywords) > 1: amount = keywords[1]


def reply_keyboard(chat_id, text):
    reply_markup ={ "keyboard": [["top 10", "top 20"], ["top 30"]], "resize_keyboard": True, "one_time_keyboard": True}
    data = {'chat_id': chat_id, 'text': text, 'reply_markup': json.dumps(reply_markup)}
    requests.post(f'{URL}{TOKEN}/sendMessage', data=data)


def dictionary_sort(dictionary):
    sorted_dict = {}
    sorted_keys = sorted(dictionary, key=dictionary.get, reverse=True)

    for w in sorted_keys:
        sorted_dict[w] = dictionary[w]

    return sorted_dict


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

                #amount = check_message(msg)
                check_message(msg, chat_id)
                #dict_for_user = dictionary_sort(volumes)
                #send_quotes(chat_id, dict_for_user, amount)


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


def pinger():
    while True:
        for user in users:
            send_quotes(user, tickers, 3)
            #send_photo(user, 'images/ENSUSDT.png')
            telegram_send_media_group('images', TOKEN, user)

        time.sleep(2)


if __name__ == '__main__':
    #volumes = analyzer.market_scoring()
    #user_update()
    TOKEN = open('screener_token.txt', 'r').read()
    URL = 'https://api.telegram.org/bot'

    tickers = {
        'BTCUSDT': 2586,
        'SOLUSDT': 99999,
        'ETHUSDT': 300,
    }

    file = open('users.yaml', 'a')
    file.close()

    users = []

    with open('users.yaml') as f:
        users = yaml.load(f, Loader=SafeLoader)
        print(users)
    f.close()

    print('ok')
    #print(volumes)
    pinger()
    #run()
    #send_quotes(254)