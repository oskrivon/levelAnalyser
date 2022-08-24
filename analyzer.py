from sys import argv
import numpy as np

from pybit import inverse_perpetual

import level_detector as ld


def str_to_bool(v):
    return str(v).lower() in ('true', '1')
    

quotation = argv[1]
volume_flag = str_to_bool(argv[2])
image_flag = str_to_bool(argv[3])

res, supp = ld.improvise_algorithm(quotation, 0.1, volume_flag, image_flag)
res_np = np.array(res)
supp_np = np.array(supp)
print(quotation, res_np[-1], supp_np[-1])