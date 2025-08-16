import pandas as pd
import numpy as np

def stock_selection(df):
    """
    Select stocks based on the refined formula conditions.
    Input: pandas DataFrame with columns: 'Open', 'High', 'Low', 'Close', 'Volume'
    Output: Boolean - True if stock meets all conditions, False otherwise
    """

    # Ensure DataFrame is sorted by date
    df = df.sort_index()

    # Calculate moving averages
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA10'] = df['Close'].rolling(window=10).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA_V5'] = df['Volume'].rolling(window=5).mean()

    # Calculate MACD manually
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_SIGNAL'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Get latest two rows
    latest = df.iloc[-1]
    previous = df.iloc[-2]

    # Condition 1: Volume amplification (current volume > 1.5 * 5-day avg volume)
    vol_amp = latest['Volume'] > latest['MA_V5'] * 1.5

    # Condition 2: Breaking previous high (current close > previous high)
    break_high = latest['Close'] > previous['High']

    # Condition 3: Moving average bull arrangement (MA5 > MA10 > MA20)
    ma_bull = latest['MA5'] > latest['MA10'] > latest['MA20']

    # Condition 4: Stock price strong operation (current close > MA5)
    price_strong = latest['Close'] > latest['MA5']

    # Condition 5: MACD golden cross
    macd_cross = (df.iloc[-2]['MACD'] < df.iloc[-2]['MACD_SIGNAL']) and (latest['MACD'] > latest['MACD_SIGNAL'])

    # Condition 6: Close to limit up price
    close_limit = latest['Close'] >= previous['Close'] * 1.099

    # Condition 7: Re-volume amplification (current volume > 2 * 5-day avg volume)
    re_vol_amp = latest['Volume'] > latest['MA_V5'] * 2

    # Condition 8: Small amplitude
    amp_small = (latest['High'] - latest['Low']) < 0.05 or ((latest['High'] - latest['Low']) / previous['Close'] < 0.05)

    # Final decision (可以改成 sum >= 5 之类的)
    return all([vol_amp, break_high, ma_bull, price_strong, macd_cross, close_limit, re_vol_amp, amp_small])
