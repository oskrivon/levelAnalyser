import requests
import json
import yaml
import time
import threading
import schedule
import datetime

import market_screener as ms
import tg_msg_preparer as msg_preparer
import tg_msg_sender as msg_sender
import tg_img_table_creator as img_creator


class ScreenerBot:
    def __init__(self):
        path = 'screener_token.txt'
        self.TOKEN = open(path, 'r').read()
        self.URL = 'https://api.telegram.org/bot'
        self.users_list = 'users.yaml'

        self.thread_go = True

        # creating file with users id (if not exist)
        file = open(self.users_list, 'a')
        file.close()

        self.users = []
        with open('users.yaml') as f:
            users = yaml.load(f, Loader=yaml.SafeLoader)
            print(users)
        f.close()

        self.screener = ms.Screener('binance')
        self.sender = msg_sender.TgSender(self.TOKEN, self.URL)

        self.msg_screening = ''
        self.msg_natrs = ''
        self.msg_fundings = ''
        self.funding_time = ''


    def get_updates(self, offset=0):
        result = requests.get(f'{self.URL}{self.TOKEN}/getUpdates?offset={offset}').json()
        return result['result']

    
    def check_message(self, msg, chat_id):
        global thread_go

        if msg == '/start':
            self.users_update(chat_id)
        
        if msg == 'help':
            msg = ('"volumes" to get the top 10 quotes with the best volumes at the moment' + '\n'+
                    '"NATRs" to get the top 10 quotes with the best NATR' + '\n' +
                    '"fundings" to get the top quotes with the best fundings rate')
            self.sender.send_message(chat_id, msg)
        
        if msg == 'stop': 
            self.thread_go = False
        
        if msg == 'go':
            self.thread_go = True

        if msg == 'volumes':
            self.sender.send_message(chat_id, 'top 10 qoutes by volume')
            self.sender.send_photo(chat_id, 'screener_results/' + 'screening' + '.png')
            self.sender.send_message(chat_id, self.msg_screening) 
        
        if msg == 'NATRes':
            self.sender.send_message(chat_id, 'top 10 qoutes by NATR')
            self.sender.send_photo(chat_id, 'screener_results/' + 'natr' + '.png')
            self.sender.send_message(chat_id, self.msg_natrs) 

        if msg == 'fundings':
            self.sender.send_message(chat_id, 'top qoutes by funding rate')
            self.sender.send_message(chat_id, self.funding_time)
            self.sender.send_photo(chat_id, 'screener_results/' + 'fundings' + '.png')
            self.sender.send_message(chat_id, self.msg_fundings)

        keywords = msg.lower().split()
        if len(keywords) > 1: amount = keywords[1]
        
        self.reply_keyboard(chat_id)


    def reply_keyboard(self, chat_id, text='select metric'):
        reply_markup = { 
            "keyboard": [
                ['volumes', 'NATRes', 'fundings'], 
                ['help']
            ], 
            "resize_keyboard": True, 
            "one_time_keyboard": True
        }
        data = {
            'chat_id': chat_id, 
            'text': text, 
            'reply_markup': json.dumps(reply_markup)
        }
        requests.post(f'{self.URL}{self.TOKEN}/sendMessage', data=data)


    def users_update(self, chat_id):
        #file = open('users.yaml', 'a+')
        if chat_id in self.users:
            print('user are exist')
        else:
            file = open(self.users_list, 'a+')
            self.users.append(chat_id)
            user = []
            user.append(chat_id)
            yaml.dump(user, file, sort_keys=False, default_flow_style=False)
            file.close()

            with open('users.yaml') as f:
                self.users = yaml.load(f, Loader=yaml.SafeLoader)
                print(self.users)
            f.close()

    
    def receiving_messages(self):
        update_id = self.get_updates()[-1]['update_id']
        while True:
            messages = self.get_updates(update_id)
            for message in messages:
                if update_id < message['update_id']:
                    chat_id = message['message']['chat']['id']
                    msg = message['message']['text']

                    #reply_keyboard(chat_id, 'select top')

                    update_id = message['update_id'] # Присваиваем ID последнего отправленного сообщения боту
                    print(f"ID пользователя: {chat_id}, Сообщение: {msg}")

                    self.check_message(msg, chat_id)



    def screening_preparer(self, screening_type, delay):
        while self.thread_go:
            if screening_type == self.screener.get_screening:
                screening = screening_type(num=10)
                
                header = 'top qoutes by volume'
                self.msg_screening = msg_preparer.msg_formatter(
                    screening, header)
                
                column_to_highlight = 'volume'

            if screening_type == self.screener.get_top_natr:
                screening = screening_type(num=10)

                header = 'top qoutes by natr'
                self.msg_natrs = msg_preparer.msg_formatter(
                    screening, header)
                
                column_to_highlight = 'natr'

            if screening_type == self.screener.get_upcoming_fundings:
                screening = screening_type(num=10)

                header = 'top qoutes by funding rates'
                self.msg_fundings = msg_preparer.msg_formatter(
                    screening, header, funding_flag=True)
                
                column_to_highlight = 'funding rate'

            screening_formated = msg_preparer.df_formatter(screening[0])
            self.funding_time = screening[1]
            img_creator.img_table_creator(screening_formated, column_to_highlight)

            time.sleep(delay)

    def alert(self):
        for user in self.users:
            self.sender.send_message(
                user, self.msg_fundings)
            self.sender.send_photo(
                user, 'screener_results/fundings.png')

    
    def alert_schedule(self):
        schedule.every().day.at("2:53:00").do(self.alert)
        schedule.every().day.at("10:53:00").do(self.alert)
        schedule.every().day.at("18:53:00").do(self.alert)

        while True:
            schedule.run_pending()
    

    def run(self):
        th_volume = threading.Thread(
            target=self.screening_preparer,
            args=(
                self.screener.get_screening, 60
            )
        )
        th_volume.daemon = True
        th_volume.start()

        th_natr = threading.Thread(
            target=self.screening_preparer,
            args=(
                self.screener.get_top_natr, 1
            )
        )
        th_natr.daemon = True
        th_natr.start()

        th_funding = threading.Thread(
            target=self.screening_preparer,
            args=(
                self.screener.get_upcoming_fundings, 60
            )
        )
        th_funding.daemon = True
        th_funding.start()

        th_alert = threading.Thread(
            target=self.alert_schedule
        )
        th_alert.daemon = True
        th_alert.start()

        self.receiving_messages()
        

if __name__ == '__main__':
    bot = ScreenerBot()
    print(bot.run())
