from sys import argv
import numpy as np

from pybit import inverse_perpetual

import level_detector as ld


quotation = argv[1]

res, supp = ld.improvise_algorithm(quotation, 0.1, False, False)
res_np = np.array(res)
supp_np = np.array(supp)
#print(quotation, res, supp)

session_unauth = inverse_perpetual.HTTP(
    endpoint="https://api.bybit.com"
)

data = session_unauth.latest_information_for_symbol(symbol=quotation)
current_price = float(data['result'][0]['last_price'])

min_resistance_distance = abs(res_np[-1] - current_price) / current_price * 100
min_support_dictance = abs(supp_np[0] - current_price) / current_price * 100

th = 0.05

if ((min_resistance_distance < min_support_dictance) and 
    (min_resistance_distance < th)): print(quotation, 'long')

if ((min_support_dictance < min_resistance_distance) and 
    (min_support_dictance < th)): print(quotation, 'short')