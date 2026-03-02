import os
os.system('pip install shoonya-api-py pyotp')

import streamlit as st
from NorenRestApiPy.NorenApi import NorenApi
import streamlit as st
from NorenRestApiPy.NorenApi import NorenApi
import pyotp
import time

# वेबसाईटचे शीर्षक आणि मांडणी
st.set_page_config(page_title="Hammer Scanner", layout="wide")
st.title("🏹 Shoonya Hammer Live Scanner")

# डाव्या बाजूला लॉगिनसाठी रिकामे बॉक्स (येथे माहिती भरू नका, वेबसाईटवर भरा)
st.sidebar.header("Login Details")
user    = st.sidebar.text_input("User ID")
pwd     = st.sidebar.text_input("Password", type="password")
vc      = st.sidebar.text_input("Vendor Code")
apikey  = st.sidebar.text_input("API Key", type="password")
totp_k  = st.sidebar.text_input("TOTP Key (Alphabetical)", type="password")

st.sidebar.divider()
multiplier = st.sidebar.slider("Hammer Ratio", 1.5, 4.0, 2.0)

# Shoonya API क्लास सेटअप
class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWSTP/', stat_host='https://api.shoonya.com/NorenWSTP/')

api = ShoonyaApiPy()

# 'Start Scanner' बटण दाबल्यावर काय व्हावे
if st.sidebar.button("Start Scanner"):
    if not all([user, pwd, vc, apikey, totp_k]):
        st.error("कृपया सर्व लॉगिन डिटेल्स भरा!")
    else:
        try:
            # TOTP जनरेट करणे
            totp = pyotp.TOTP(totp_k).now()
            
            # लॉगिन प्रोसेस
            ret = api.login(userid=user, password=pwd, twoFA=totp, vendor_code=vc, api_key=apikey, imei='abc1234')
            
            if ret and ret['stat'] == 'Ok':
                st.success("✅ Shoonya शी कनेक्शन यशस्वी!")
                placeholder = st.empty()
                
                # लाइव्ह स्कॅनिंग लूप
                while True:
                    # Nifty 50 (Token: 26000) चा ५ मिनिटांचा डेटा मिळवणे
                    last_candle = api.get_time_price_series(exchange='NSE', token='26000', interval=5)
                    
                    if last_candle and len(last_candle) > 0:
                        c = last_candle[0]
                        o, h, l, close = float(c['into']), float(c['inth']), float(c['intl']), float(c['inc'])
                        
                        # हॅमर कॅन्डलचे लॉजिक
                        body = abs(o - close)
                        lower_shadow = min(o, close) - l
                        upper_shadow = h - max(o, close)
                        
                        if body > 0 and lower_shadow >= (multiplier * body) and upper_shadow < (body * 0.5):
                            placeholder.warning(f"🚨 ALERT: Hammer Found! Price: {close}")
                            st.balloons()
                        else:
                            placeholder.info(f"स्कॅनिंग सुरू आहे... सध्याची किंमत: {close}")
                    
                    time.sleep(60) # दर १ मिनिटाने डेटा अपडेट होईल
            else:
                st.error(f"लॉगिन अयशस्वी: {ret.get('emsg', 'Unknown Error')}")
        except Exception as e:
            st.error(f"Error: {e}")
