import json
import time
import pandas as pd

from ibapi.contract import Contract

from .fundamental import get_fundamental_analysis
from .technical import get_technical_action
from ..ib.client import ib
from ..utils import build_response


async def get_chart_data(symbol: str, currency: str):
    contract = Contract()
    contract.symbol = symbol.upper()
    contract.secType = 'CASH'
    contract.exchange = 'IDEALPRO'
    contract.currency = currency.upper()
    ib.reqHistoricalData(1, contract, '', '2 D', '1 hour', 'BID', 1, 2, False, [])
    time.sleep(5)  # sleep to allow enough time for data to be returned
    df = pd.DataFrame(ib.data, index=None, columns=['Date', 'High', 'Low', 'Open',
                                                    'Close'])
    df['Date'] = pd.to_datetime(df['Date'], unit='s')
    df_json = df.to_json(orient='records', date_format='iso')
    ib.data = []
    return df_json


async def get_indicator_val(symbol: str, currency: str):
    fundamental = await get_fundamental_analysis()
    fundamental = fundamental[fundamental["pair"] == f"{symbol.lower()}/{currency.lower()}"]
    fundamental_action = fundamental.action.value_counts(normalize=True).get("sell", 0)
    technical_action = await get_technical_action(symbol, currency)
    sum_ = round((fundamental_action + technical_action) / 2, 2)
    return sum_
