import websocket

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("### connected ###")

if __name__ == "__main__":
    #ws = websocket.WebSocketApp("wss://stream.binance.com:9443/stream?streams=ltcbtc@aggTrade/ethbtc@aggTrade",
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/ltcbtc@aggTrade/ethbtc@aggTrade",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()