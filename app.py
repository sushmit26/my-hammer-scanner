import streamlit as st
import yfinance as yf
import pandas as pd

# १. पेज सेटिंग
st.set_page_config(page_title="Nifty 200 Multi-Timeframe Screener", page_icon="📈", layout="wide")

st.title("📈 Nifty 200 Hammer Screener (Multi-Timeframe)")

# २. साइडबार - सेटिंग्स
st.sidebar.header("Screener Settings")

# Multiplier: Slider ऐवजी Number Input वापरले आहे
multiplier = st.sidebar.number_input("Shadow Multiplier टाका (उदा. 2.0)", min_value=1.0, max_value=10.0, value=2.5, step=0.1)

# Timeframe निवडण्यासाठी Dropdown
timeframe_map = {
    "1 Hour": {"interval": "60m", "period": "2y"},
    "2 Hours": {"interval": "120m", "period": "2y"},
    "3 Hours": {"interval": "180m", "period": "2y"}, # टीप: 3h साठी आपण 1h चा डेटा वापरून लॉजिक लावू शकतो, सध्या इथे जवळचे पर्याय दिले आहेत.
    "4 Hours": {"interval": "240m", "period": "2y"},
    "1 Day": {"interval": "1d", "period": "5y"},
    "1 Week": {"interval": "1wk", "period": "max"},
    "1 Month": {"interval": "1mo", "period": "max"}
}
selected_tf = st.sidebar.selectbox("Timeframe निवडा", list(timeframe_map.keys()))

# ३. NIFTY 200 ची लिस्ट
nifty_200_tickers = [
    "ABB.NS", "ACC.NS", "ADANIENT.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", "AMBUJACEM.NS", "APOLLOHOSP.NS", 
    "ASIANPAINT.NS", "AUROPHARMA.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", 
    "BEL.NS", "BHARTIARTL.NS", "BIOCON.NS", "BPCL.NS", "BRITANNIA.NS", "CANBK.NS", "CHOLAFIN.NS", 
    "CIPLA.NS", "COALINDIA.NS", "COLPAL.NS", "CONCOR.NS", "DLF.NS", "DABUR.NS", "DIVISLAB.NS", 
    "DRREDDY.NS", "EICHERMOT.NS", "GAIL.NS", "GLENMARK.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", 
    "HAVELLS.NS", "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "IDFCFIRSTB.NS", 
    "ITC.NS", "INDHOTEL.NS", "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", 
    "LTIM.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS", "PIDILITIND.NS", 
    "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS", "SUNPHARMA.NS", "TATACOMM.NS", 
    "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TITAN.NS", 
    "TRENT.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS", "ZOMATO.NS"
]

def check_hammer(ticker, mult, interval, period):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty: return None
        
        last_row = df.iloc[-1]
        open_p, close_p, high_p, low_p = float(last_row['Open']), float(last_row['Close']), float(last_row['High']), float(last_row['Low'])
        
        body = abs(close_p - open_p)
        lower_shadow = min(open_p, close_p) - low_p
        upper_shadow = high_p - max(open_p, close_p)
        
        if body == 0: body = 0.01 # Division by zero टाळण्यासाठी
        
        # तुमची मूळ Hammer Condition
        if lower_shadow > (body * mult) and upper_shadow < (body * 0.5):
            return round(close_p, 2)
        return False
    except:
        return None

# ४. स्कॅनिंग प्रोसेस
if st.button(f"🔍 {selected_tf} साठी Nifty 200 स्कॅन करा"):
    st.write(f"निवडलेला काळ: **{selected_tf}** | Multiplier: **{multiplier}**")
    progress_bar = st.progress(0)
    found_stocks = []
    
    settings = timeframe_map[selected_tf]
    
    for index, stock in enumerate(nifty_200_tickers):
        progress_bar.progress((index + 1) / len(nifty_200_tickers))
        price = check_hammer(stock, multiplier, settings['interval'], settings['period'])
        if price:
            found_stocks.append({"Stock Symbol": stock, "LTP": price, "Timeframe": selected_tf})
            
    if found_stocks:
        st.success(f"धडाका! {len(found_stocks)} स्टॉक्समध्ये Hammer सापडली आहे.")
        st.table(pd.DataFrame(found_stocks))
    else:
        st.info(f"सध्या {selected_tf} टाइमफ्रेममध्ये कोणताही स्टॉक निकषात बसत नाही.")

st.divider()
st.caption("Disclaimer: हा स्क्रीनर फक्त शैक्षणिक हेतूसाठी आहे.")
