import websocket
import requests
import threading
import json

REST_URL = "https://fapi.binance.com/fapi/v1/depth?symbol={}&limit=1000"
WEBSOCKET_URL = "wss://fstream.binance.com/ws/{}@depth@100ms"

class Orderbook:
    def __init__(self, symbol: str):
        self._socket = WEBSOCKET_URL.format(symbol)
        self._rest = REST_URL.format(symbol)
        self._ws = websocket.WebSocketApp(self._socket, on_message=self.on_message, on_close=self.on_close)
        self._bids = {}
        self._asks = {}
        self._last_update_id = 0
        self._prev_u = None
        self._lock = False

    def _get_snapshot(self):
        """Reset _bids and _asks to a snapshot of the current orderbook and update last_update_id."""
        r = requests.get(self._rest)
        self._lock = True
        data = json.loads(r.text)
        
        self._last_update_id = data["lastUpdateId"]

        self._bids = {float(price): float(qty) for price, qty in data["bids"]}
        self._asks = {float(price): float(qty) for price, qty in data["asks"]}
        self._lock = False

    def on_close(self, ws):
        print("Session closed.")

    def on_message(self, ws, message_str):
        while self._lock:
            pass

        message = json.loads(message_str)
        if message["u"] >= self._last_update_id:
            #Loop through price levels and quantities for bid and ask events and update quantities
            for price_level, qty in message["b"]:
                if float(qty) == 0:
                    self._bids.pop(float(price_level), None)
                else:
                    self._bids[float(price_level)] = float(qty)

            for price_level, qty in message["a"]:
                if float(qty) == 0:
                    self._asks.pop(float(price_level), None)
                else:
                    self._asks[float(price_level)] = float(qty)

        if self._prev_u != None and self._prev_u != message["pu"]:
            print("Orderbook out of sync, grabbing new snapshot")
            self._get_snapshot()

        self._prev_u = message["u"]

    def connect(self):
        wst = threading.Thread(target=self._ws.run_forever)
        wst.daemon = True
        wst.start()
        self._get_snapshot()

    def get_quotes(self) -> tuple[float, float]:
        """Return best bid and ask"""
        return max(self._bids.keys()), min(self._asks.keys())
    
    def get_bids(self) -> dict:
        """Return bids"""
        return self._bids
    
    def get_asks(self) -> dict:
        """Return asks"""
        return self._asks