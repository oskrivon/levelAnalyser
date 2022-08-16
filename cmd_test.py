from sys import argv
import time

import level_detector as ld

q = argv[1]
ld.improvise_algorithm(q, 0.1, False, True)