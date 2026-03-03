import streamlit as st
import yfinance as yf
import pandas as pd

# UI सेटिंग्स
st.set_page_config(page_title="Hammer Screener", layout="wide")
st.title("🔨 Hammer Candle Stock Screener")

# साइडबार - इनपुट सेटिंग्स
st.sidebar.header("Settings")
multiplier = st.sidebar.slider("Shadow Multiplier (Body च्या तुलनेत)", 1.5, 5.0, 2.0)
history = st.sidebar.selectbox("किती दिवसांचा डेटा हवा?", ["1mo", "3mo", "6mo"])

# स्टॉक्सची लिस्ट (तुम्ही यात अजून नावे जोडू शकता)
nifty_stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "SBIN.NS"]

def check_hammer(ticker, mult):
    try:
        df = yf.download(ticker, period="5d", interval="1d", progress=False)
        if df.empty: return None
        
        last_row = df.iloc[-1]
        open_p, close_p, high_p, low_p = last_row['Open'], last_row['Close'], last_row['High'], last_row['Low']
        
        body = abs(close_p - open_p)
        lower_shadow = min(open_p, close_p) - low_p
        upper_shadow = high_p - max(open_p, close_p)
        
        # Hammer Logic: 
        # 1. Lower Shadow > (Body * Multiplier)
        # 2. Upper Shadow खूप लहान असावी
        if lower_shadow > (body * mult) and upper_shadow < (body * 0.5) and body > 0:
            return True
        return False
    except:
        return None

# मुख्य स्क्रीनवर बटन
if st.button("स्टॉक्स स्कॅन करा"):
    st.write(f"स्कॅनिंग सुरू आहे... (Multiplier: {multiplier}x)")
    found_stocks = []
    
    for stock in nifty_stocks:
        if check_hammer(stock, multiplier):
            found_stocks.append(stock)
            
    if found_stocks:
        st.success(f"खालील स्टॉक्समध्ये Hammer पॅटर्न दिसला आहे:")
        for s in found_stocks:
            st.write(f"✅ **{s}**")
    else:
        st.info("सध्या कोणत्याही स्टॉकमध्ये असा पॅटर्न नाही.")
