import datetime
from pathlib import Path
from unicodedata import name
import yaml


class Logger:
    def __init__(self, quotation):
        self.dirname = 'trades/'
        self.quotation = quotation


    def __update(self, info, mode):
        self.log = open(self.file_name, mode)
        yaml.dump(info, self.log, sort_keys=False, default_flow_style=False)
        self.log.close()


    def create(self):
        open_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H-%M')
        self.file_name = self.dirname + self.quotation + ' ' + open_time + '.yaml'
        info = {'quotation': self.quotation}

        self.__update(info, 'w+')
    

    def update(self, **kwargs):
        self.__update(kwargs, 'a+')


    def log_open_trade(self, date, side, buy_price, stop_loss, 
                    quantile_50, quantile_75, volume, open_interest):
        open_trade = (str(date) + '\n' + 
                    side + '\n' + 
                    'buy price: ' + str(buy_price) + '\n' + 
                    'stop loss: ' + str(stop_loss) + '\n' + 
                    '50-quantile: ' + str(quantile_50) + '\n' +
                    '75-quantile: ' + str(quantile_75) + '\n' +
                    'volume: ' + str(volume) + '\n'+ 
                    'open interest: ' + str(open_interest) + '\n')
        return open_trade


    def log_close_trade(self, date, sell_price, profit):
        close_trade = (str(date) + '\n' + 
                    'sell price: ' + str(sell_price) + '\n' + 
                    'profit: ' + str(profit))
        return close_trade


    trade_info = {'date': 12345, 
                'side': 'short',
                'buy price': 20
                }

# test
if __name__ == "__main__":
    log = Logger('BTCUSDT')
    log.create()
    info = {
        'open time': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'side': 'short',
        'buy price': 12345,
        'stop loss': 515151,
        'volume': 48484848,
        'open interest': 58741.36985,
        'quantile 50': 999,
        'quantile 75': 000
    }
    log.update(**info)

    info = {
        'xxx': 25,
        'zzz': 0.258741
    }
    log.update(**info)