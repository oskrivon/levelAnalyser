from sys import argv
import numpy as np
import datetime
from pathlib import Path

dirname = 'trades/'
quotation = 'xxx'

date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H-%M')

path = dirname + quotation + ' ' + date + '.txt'

file = Path(path)
file.touch(exist_ok=True)
f = open(file, 'w')

f.write('open_trade' + '\n')

f.close()