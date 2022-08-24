def log_open_trade(date, side, buy_price, stop_loss):
    open_trade = (str(date) + '\n' + 
                  side + '\n' + 
                  'buy price: ' + str(buy_price) + '\n' + 
                  'stop loss ' + str(stop_loss) + '\n')
    return open_trade

def log_close_trade(date, sell_price, profit):
    close_trade = (str(date) + '\n' + 
                   'sell price: ' + str(sell_price) + '\n' + 
                   'profit: ' + str(profit))
    return close_trade