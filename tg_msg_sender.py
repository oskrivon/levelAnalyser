import requests
import os
import json


class TgSender:
    def __init__(self, token, url):
        self.TOKEN = token
        self.URL = url


    def send_message(self, chat_id, text):
        requests.get(f'{self.URL}{self.TOKEN}/sendMessage?chat_id={chat_id}&text={text}')


    def send_photo(self, chat_id, path):
        files = {'photo': open(path, 'rb')}
        requests.post(f'{self.URL}{self.TOKEN}/sendPhoto?chat_id={chat_id}', files=files)


    def telegram_send_media_group(self, chat_id, path):    
        url = "https://api.telegram.org/bot" + self.TOKEN + "/sendMediaGroup"
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