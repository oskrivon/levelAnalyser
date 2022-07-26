import os
import json
import requests

TOKEN = open('telegram_key.txt', 'r').read()
channel_id = '@level_signals'

def telegram_message_send(text: str, token):
    url = 'https://api.telegram.org/bot' + token + '/sendMessage'
    channel_id = '@level_signals'

    data = {'chat_id': channel_id, 'text': text}

    r = requests.post(url, data=data)

def telegram_photo_send(path, token):
    url = 'https://api.telegram.org/bot' +  token + '/sendPhoto'
    channel_id = '@level_signals'

    files = {'photo': open(path, 'rb')}
    data = {'chat_id' : "@level_signals"}

    r = requests.post(url, files=files, data=data)

def telegram_send_media_group(path, token):    
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
            'chat_id': channel_id, 
            'media': media
            }

    r = requests.post(url, params= params, files= files)