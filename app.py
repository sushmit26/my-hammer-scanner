import streamlit as st
import yfinance as yf
import pandas as pd

# १. पेज सेटिंग
st.set_page_config(page_title="Nifty 200 Pro Screener", page_icon="📈", layout="wide")
st.title("📈 Nifty 200 Advanced Hammer Screener")

# २. साइडबार - इनपुट सेटिंग्स
st.sidebar.header("Screener Settings")

# Multiplier: स्लाइडर ऐवजी नंबर इनपुट
multiplier = st.sidebar.number_input("Shadow Multiplier टाका", min_value=1.0, max_value=10.0, value=2.0, step=0.1)

# Timeframes
timeframe_map = {
    "1 Hour": {"interval": "60m", "period": "2y"},
    "2 Hours": {"interval": "120m", "period": "2y"},
    "3 Hours": {"interval": "180m", "period": "2y"},
    "1 Day": {"interval": "1d", "period": "5y"},
    "1 Week": {"interval": "1wk", "period": "max"},
    "1 Month": {"interval": "1mo", "period": "max"}
}
selected_tf = st.sidebar.selectbox("Timeframe निवडा", list(timeframe_map.keys()))

# ३. NIFTY 200 प्रमुख स्टॉक्स (प्रातिनिधिक लिस्ट)
nifty_200_tickers = [
    "ABB.NS", "ACC.NS", "ADANIENT.NS", "ADANIPORTS.NS", "ASIANPAINT.NS", "AXISBANK.NS", 
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BEL.NS", "BHARTIARTL.NS", "BPCL.NS", "BRITANNIA.NS", 
    "CIPLA.NS", "COALINDIA.NS", "DLF.NS", "DABUR.NS", "DRREDDY.NS", "EICHERMOT.NS", 
    "GAIL.NS", "HCLTECH.NS", "HDFCBANK.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", 
    "ICICIBANK.NS", "ITC.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS", 
    "MARUTI.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBIN.NS", "SUNPHARMA.NS", 
    "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS"
]

def check_custom_hammer(ticker, mult, interval, period):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty: return None
        
        last = df.iloc[-1]
        o, c, h, l = float(last['Open']), float(last['Close']), float(last['High']), float(last['Low'])
        
        # तुमच्या इमेजमधील चार्ट इंक कंडिशन्स:
        # 1. (Open - Low) >= (Close - Open) * Multiplier
        cond1 = (o - l) >= (abs(c - o) * mult)
        
        # 2. (High - Close) <= (High - Low) * 0.1
        cond2 = (h - max(o, c)) <= ((h - l) * 0.1)
        
        # 3. Close > Open (Bullish Hammer)
        cond3 = c > o
        
        if cond1 and cond2 and cond3:
            return round(c, 2)
        return False
    except:
        return None

# ४. स्कॅनिंग बटण
if st.button(f"🔍 {selected_tf} स्कॅन करा"):
    st.write(f"निकष: **(Open-Low) >= (Body * {multiplier})** आणि **Small Upper Shadow**")
    progress_bar = st.progress(0)
    found_stocks = []
    
    settings = timeframe_map[selected_tf]
    
    for index, stock in enumerate(nifty_200_tickers):
        progress_bar.progress((index + 1) / len(nifty_200_tickers))
        price = check_custom_hammer(stock, multiplier, settings['interval'], settings['period'])
        if price:
            found_stocks.append({"Stock": stock, "Price": price, "Timeframe": selected_tf})
            
    if found_stocks:
        st.success(f"सापडले! {len(found_stocks)} स्टॉक्स कंडिशनमध्ये बसत आहेत.")
        st.table(pd.DataFrame(found_stocks))
    else:
        st.info("या टाइमफ्रेममध्ये सध्या कोणताही स्टॉक सापडला नाही.")

st.divider()
st.caption("Chartink लॉजिकवर आधारित स्क्रीनर.")
