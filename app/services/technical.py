import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
import time

from tensorflow.keras.models import load_model
from ibapi.contract import Contract

from ..ib.client import ib

seed = 42
np.random.seed(seed)
tf.random.set_seed(seed)

models = {}
scalers = {}


def get_series(symbol: str, currency: str):
    series = []
    contract = Contract()
    contract.symbol = symbol.upper()
    contract.secType = 'CASH'
    contract.exchange = 'IDEALPRO'
    contract.currency = currency.upper()
    ib.reqHistoricalData(1, contract, '', '20 D', '1 hour', 'BID', 1, 2, False, [])
    time.sleep(5)
    for d in ib.data[-258:]:
        series.append(str((d[1] + d[2]) / 2))
    data = ','.join(series)
    ib.data = []
    return data[:-1]


def get_model_and_scaler(ticker, batch_size, window_size, ma_periods):
    key = f'{ticker}-{batch_size}-{window_size}-{ma_periods}'
    if key not in models:
        models[key] = load_model(f'app/resources/{key}')
    if key not in scalers:
        scalers[key] = joblib.load(f'app/resources/{key}.bin')
    return models[key], scalers[key]


def get_dataframe(past_series_str, window_size, ma_periods, scaler):
    past_series = np.array(past_series_str.split(','))
    past_series_len = len(past_series)
    if (past_series_len != window_size + ma_periods):
        raise Exception(
            f'past_series_len != window_size + ma_periods. {past_series_len} != {window_size} + {ma_periods}')
    past_series = past_series.astype(np.float)
    df = pd.DataFrame({'HLAvg': past_series})
    df['MA'] = df['HLAvg'].rolling(window=ma_periods).mean()  # Simple Moving Average
    df.dropna(how='any', inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['Returns'] = np.log(df['MA'] / df['MA'].shift(1))  # Log Returns
    df.dropna(how='any', inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['Scaled'] = scaler.transform(df[['Returns']].values)
    return df


def is_support(df, i):
    support = df['Low'][i] < df['Low'][i - 1] < df['Low'][i - 2] and df['Low'][i] < df['Low'][i + 1] < df['Low'][i + 2]
    return support


def is_resistance(df, i):
    resistance = df['High'][i] > df['High'][i - 1] > df['High'][i - 2] and df['High'][i] > df['High'][i + 1] > \
                 df['High'][i + 2]
    return resistance


def rsi(df, periods=14, ema=True):
    close_delta = df['close'].diff()

    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)

    if ema == True:
        ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
        ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    else:
        ma_up = up.rolling(window=periods, adjust=False).mean()
        ma_down = down.rolling(window=periods, adjust=False).mean()

    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi


async def get_technical_action(symbol, currency):
    batch_size = 32
    window_size = 256
    ma_periods = 2
    abs_pips = 0.0008
    pred_size = 4

    ticker = f"{symbol.lower()}{currency.lower()}"
    series = get_series(symbol, currency)
    model, scaler = get_model_and_scaler(ticker, batch_size, window_size, ma_periods)
    df = get_dataframe(series, window_size, ma_periods, scaler)

    y_ma = float(df['MA'].iloc[-1])
    top_price = y_ma + abs_pips
    bottom_price = y_ma - abs_pips

    X = [df['Scaled'].values]
    y = []
    for _ in range(pred_size):
        X = np.asarray(X)
        X = np.reshape(X, (1, window_size, 1))
        y_pred_scaled = model.predict(X)
        y_return = scaler.inverse_transform(y_pred_scaled)
        y_ma = y_ma * np.exp(y_return)  # Reverse Log Returns

        if (y_ma >= top_price):
            return 0

        if (y_ma <= bottom_price):
            return 1

        y.append(float(y_ma))
        # Remove first item in the list
        X = np.delete(X, 0)
        # Add the new prediction to the end
        X = np.append(X, y_pred_scaled)

    return 0.5
