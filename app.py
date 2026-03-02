import streamlit as st
from NorenRestApiPy.NorenApi import NorenApi
import pyotp
import time

st.set_page_config(page_title="Hammer Scanner", layout="wide")
st.title("🏹 My Live Hammer Scanner")

# --- Sidebar Settings ---
st.sidebar.header("Settings")
ratio = st.sidebar.slider("Hammer Ratio", 1.5, 4.0, 2.0)
interval = st.sidebar.selectbox("Timeframe", [1, 5, 15, 30])

# --- Shoonya Login Inputs ---
user = st.sidebar.text_input("User ID")
pwd = st.sidebar.text_input("Password", type="password")
vc = st.sidebar.text_input("Vendor Code (VC)")
apikey = st.sidebar.text_input("API Key", type="password")
totp_key = st.sidebar.text_input("TOTP Key (Alphabetical)", type="password")

class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWSTP/', stat_host='https://api.shoonya.com/NorenWSTP/')

api = ShoonyaApiPy()

if st.sidebar.button("Connect & Start Scan"):
    if not all([user, pwd, vc, apikey, totp_key]):
        st.error("कृपया सर्व लॉगिन डिटेल्स भरा!")
    else:
        # TOTP जनरेट करणे
        totp = pyotp.TOTP(totp_key).now()
        
        # लॉगिन करणे
        ret = api.login(userid=user, password=pwd, twoFA=totp, vendor_code=vc, api_key=apikey, imei='abc1234')
        
        if ret and ret['stat'] == 'Ok':
            st.success(f"✅ लॉगिन यशस्वी! {ratio} रेशोवर स्कॅनिंग सुरू आहे...")
            
            placeholder = st.empty()
            while True:
                # निफ्टी ५० (Token: 26000) चा डेटा मिळवणे
                last_candle = api.get_time_price_series(exchange='NSE', token='26000', interval=interval)
                
                if last_candle and len(last_candle) > 0:
                    c = last_candle[0]
                    o, h, l, close = float(c['into']), float(c['inth']), float(c['intl']), float(c['inc'])
                    
                    # हॅमर लॉजिक
                    body = abs(o - close)
                    lower_shadow = min(o, close) - l
                    upper_shadow = h - max(o, close)
                    
                    if body > 0 and lower_shadow >= (ratio * body) and upper_shadow < (body * 0.5):
                        with placeholder.container():
                            st.warning(f"🚨 HAMMER FOUND! Price: {close}")
                            st.balloons()
                    else:
                        placeholder.info(f"स्कॅनिंग सुरू आहे... शेवटची किंमत: {close}")
                
                time.sleep(60) # दर १ मिनिटाने अपडेट
        else:
            st.error(f"लॉगिन अयशस्वी: {ret['emsg'] if ret else 'Unknown Error'}")
