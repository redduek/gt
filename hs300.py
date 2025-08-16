import streamlit as st
import pandas as pd
import numpy as np
import talib
import yfinance as yf

st.set_page_config(page_title="A股策略选股", layout="centered")

st.title("📈 A股策略选股 Demo")

# 输入股票代码
ticker = st.text_input("请输入股票代码（如：'000001.SS' 表示上证指数，'000300.SS' 表示沪深300）", "000300.SS")

# 设置回测区间
period = st.selectbox("选择数据区间", ["3mo", "6mo", "1y", "2y"], index=0)

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

# 抓取数据
if st.button("开始选股"):
    try:
        df = yf.download(ticker, period=period, interval="1d")
        if df.empty:
            st.error("未能获取数据，请检查股票代码是否正确")
        else:
            st.write("最近数据：", df.tail())

            result = stock_selection(df)
            if result:
                st.success("✅ 符合策略条件！")
            else:
                st.warning("❌ 不符合策略条件")

    except Exception as e:
        st.error(f"运行出错: {e}")
