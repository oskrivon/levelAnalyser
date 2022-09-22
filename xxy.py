import websocket
import json

def on_message(ws, message):
    fundings_json = json.loads(message)
    funding = [x['r'] for x in fundings_json if x['s'] == 'BTCUSDT']
    print(funding)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("### connected ###")

if __name__ == "__main__":
    #ws = websocket.WebSocketApp("wss://stream.binance.com:9443/stream?streams=ltcbtc@aggTrade/ethbtc@aggTrade",
    ws = websocket.WebSocketApp("wss://fstream.binance.com/ws/!markPrice@arr@1s",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()