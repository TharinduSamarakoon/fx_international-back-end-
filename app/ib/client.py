import threading

from ibapi.client import EClient
from ibapi.wrapper import EWrapper


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []

    def historicalData(self, reqId, bar):
        self.data.append([bar.date, bar.high, bar.low, bar.open, bar.close])


ib = IBapi()
ib.connect('127.0.0.1', 7497, 123)
api_thread = threading.Thread(target=ib.run, daemon=True)
api_thread.start()
