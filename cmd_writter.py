import os

command1 = "python price_ticker.py ANTUSDT &" #command to be executed
command2 = "python price_ticker.py ALICEUSDT &"

#print('command: ', command)
os.system(command1)
os.system(command2)
#the method returns the exit status

#print("Returned Value: ", res)