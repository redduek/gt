import streamlit as st
import pandas as pd
import numpy as np
import talib

st.title("📈 A股策略选股 Demo")

# 上传数据
uploaded_file = st.file_uploader("请上传股票数据 CSV 文件 (需包含 Date, Open, High, Low, Close, Volume)", type="csv")

def stock_selection(df):
    df = df.sort_index()
    df['MA5'] = talib.SMA(df['Close'], timeperiod=5)
    df['MA10'] = talib.SMA(df['Close'], timeperiod=10)
    df['MA20'] = talib.SMA(df['Close'], timeperiod=20)
    df['MA_V5'] = talib.SMA(df['Volume'], timeperiod=5)
    df['MACD'], df['MACD_SIGNAL'], _ = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    vol_amp = latest['Volume'] > latest['MA_V5'] * 1.5
    break_high = latest['Close'] > previous['High']
    ma_bull = latest['MA5'] > latest['MA10'] > latest['MA20']
    price_strong = latest['Close'] > latest['MA5']
    macd_cross = (df.iloc[-2]['MACD'] < df.iloc[-2]['MACD_SIGNAL']) and (latest['MACD'] > latest['MACD_SIGNAL'])
    close_limit = latest['Close'] >= previous['Close'] * 1.099
    re_vol_amp = latest['Volume'] > latest['MA_V5'] * 2
    amp_small = (latest['High'] - latest['Low']) < 0.05 or ((latest['High'] - latest['Low']) / previous['Close'] < 0.05)

    return all([vol_amp, break_high, ma_bull, price_strong, macd_cross, close_limit, re_vol_amp, amp_small])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("原始数据：", df.tail())

    try:
        result = stock_selection(df)
        if result:
            st.success("✅ 股票符合策略条件！")
        else:
            st.warning("❌ 股票不符合策略条件")
    except Exception as e:
        st.error(f"运行出错: {e}")
