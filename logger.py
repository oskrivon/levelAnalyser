import datetime
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