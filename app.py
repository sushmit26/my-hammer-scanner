import streamlit as st
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="Correct Hammer Screener", layout="wide")
st.title("🎯 Exact Chartink Hammer Screener")

# साइडबार सेटिंग्ज
multiplier = st.sidebar.number_input("Shadow Multiplier (Number 2)", min_value=1.0, value=2.0, step=0.1)
# इमेजमध्ये Weekly आहे म्हणून 1wk निवडले आहे
selected_tf = st.sidebar.selectbox("Timeframe (Chartink प्रमाणे निवडा)", ["1 Week", "1 Day", "1 Hour"])

tf_map = {"1 Week": "1wk", "1 Day": "1d", "1 Hour": "60m"}
period_map = {"1 Week": "5y", "1 Day": "2y", "1 Hour": "2y"}

# तुमची पूर्ण ५०० स्टॉक्सची लिस्ट इथे ठेवा
tickers =[
    "360ONE.NS", "3MINDIA.NS", "ABB.NS", "ACC.NS", "AIAENG.NS", "APLAPOLLO.NS", "AUBANK.NS", "AADHARHFC.NS", "AARTIIND.NS", "AAVAS.NS", 
    "ABBOTINDIA.NS", "ACE.NS", "ADANIENSOL.NS", "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", "ADANITOTALGAS.NS", "AWL.NS", "ADEPRO.NS", 
    "ADVENZYMES.NS", "AEGISLOG.NS", "AETHER.NS", "AFFLE.NS", "AJANTPHARM.NS", "AKEMS.NS", "AKZOINDIA.NS", "ALKYLAMINE.NS", "ALLCARGO.NS", "ALOKINDS.NS", 
    "ARE&M.NS", "AMBER.NS", "AMBUJACEM.NS", "ANANTRAJ.NS", "ANGELONE.NS", "APARINDS.NS", "APOLLOHOSP.NS", "APOLLOTYRE.NS", "APTUS.NS", "AREVAV.NS", 
    "ASHOKLEY.NS", "ASIANPAINT.NS", "ASTERDM.NS", "ASTRAZEN.NS", "ASTRAL.NS", "ATUL.NS", "AUROPHARMA.NS", "AVANTIFEED.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", 
    "BAJFINANCE.NS", "BAJAJFINSV.NS", "BAJAJHLDNG.NS", "BALAMINES.NS", "BALKRISIND.NS", "BALRAMCHIN.NS", "BANDHANBNK.NS", "BANKBARODA.NS", "BANKINDIA.NS", "MAHABANK.NS", 
    "BATAINDIA.NS", "BAYERCROP.NS", "BERGEPAINT.NS", "BDL.NS", "BEL.NS", "BHARATFORG.NS", "BHEL.NS", "BPCL.NS", "BHARTIARTL.NS", "BIOCON.NS", 
    "BIRLACORPN.NS", "BSOFT.NS", "BLS.NS", "BLUEDART.NS", "BLUESTARCO.NS", "BBTC.NS", "BORORENEW.NS", "BOSCHLTD.NS", "BRIGADE.NS", "BRITANNIA.NS", 
    "MAPMYINDIA.NS", "BSE.NS", "CESC.NS", "CGPOWER.NS", "CIEINDIA.NS", "CRISIL.NS", "CSBBANK.NS", "CAMPUS.NS", "CANFINHOME.NS", "CANBK.NS", 
    "CAPLIPOINT.NS", "CGCL.NS", "CARBORUNIV.NS", "CASTROLIND.NS", "CEATLTD.NS", "CENTRALBK.NS", "CDSL.NS", "CENTURYPLY.NS", "CENTURYTEX.NS", "CERA.NS", 
    "CHALET.NS", "CHAMBLFERT.NS", "CHMSBL_P.NS", "CHENNPETRO.NS", "CHOLAHLDNG.NS", "CHOLAFIN.NS", "CIPLA.NS", "CUB.NS", "CLEAN.NS", "COALINDIA.NS", 
    "COCHINSHIP.NS", "COFORGE.NS", "COLPAL.NS", "CAMS.NS", "CONCOR.NS", "COROMANDEL.NS", "CRAFTSMAN.NS", "CREDITACC.NS", "CROMPTON.NS", "CUMMINSIND.NS", 
    "CYIENT.NS", "DCMSHRIRAM.NS", "DLF.NS", "DOMS.NS", "DABUR.NS", "DALBHARAT.NS", "DATAPATTNS.NS", "DEEPAKFERT.NS", "DEEPAKNTR.NS", "DELHIVERY.NS", 
    "DEVYANI.NS", "DIVISLAB.NS", "DIXON.NS", "DRREDDY.NS", "EIDPARRY.NS", "EIHOTEL.NS", "EPL.NS", "EASEMYTRIP.NS", "EICHERMOT.NS", "ELECON.NS", 
    "ELGIEQUIP.NS", "EMAMILTD.NS", "ENDURANCE.NS", "ENGINERSIN.NS", "ENVAIR.NS", "ESCORTS.NS", "EXIDEIND.NS", "FSL.NS", "FSNREMS.NS", "FEDERALBNK.NS", 
    "FACT.NS", "FINEORG.NS", "FINCABLES.NS", "FINPIPE.NS", "FLUOROCHEM.NS", "FORTIS.NS", "GRINFRA.NS", "GAIL.NS", "GAMMONIND.NS", "GMRINFRA.NS", 
    "GNA.NS", "GOCLCORP.NS", "GPIL.NS", "GRSE.NS", "GARDENREACH.NS", "GATEWAY.NS", "GEPIL.NS", "GESHIP.NS", "GENUSPOWER.NS", "GLAND.NS", 
    "GLAXO.NS", "GLENMARK.NS", "GMM_PFAUDL.NS", "GOCOLORS.NS", "GODFRYPHLP.NS", "GODREJAGRO.NS", "GODREJCP.NS", "GODREJIND.NS", "GODREJPROP.NS", "GRANULES.NS", 
    "GRAPHITE.NS", "GRASIM.NS", "GRAVITA.NS", "GREAVESCOT.NS", "GRINDWELL.NS", "GUJALKALI.NS", "GUJGASLTD.NS", "GNFC.NS", "GPPL.NS", "GSFC.NS", 
    "GSPL.NS", "GULFOILLUB.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HMT.NS", "HFCL.NS", "HAPPSTMNDS.NS", "HAVELLS.NS", "HEROMOTOCO.NS", 
    "HINDALCO.NS", "HAL.NS", "HINDCOPPER.NS", "HINDPETRO.NS", "HINDUNILVR.NS", "HINDZINC.NS", "HOMEFIRST.NS", "HONAUT.NS", "HUDCO.NS", "ICICIBANK.NS", 
    "ICICIGI.NS", "ICICIPRULI.NS", "ISEC.NS", "IDBI.NS", "IDFCFIRSTB.NS", "IDFC.NS", "IFCI.NS", "IIFL.NS", "IRB.NS", "IRCON.NS", 
    "IRCTC.NS", "IRFC.NS", "ITI.NS", "INDIA_GLYCO.NS", "INDIACEM.NS", "IBREALEST.NS", "INDIAMART.NS", "INDIANB.NS", "IEX.NS", "INDHOTEL.NS", 
    "IOC.NS", "IOB.NS", "IRCTC.NS", "INDUSINDBK.NS", "INDUSTOWER.NS", "INFIBEAM.NS", "INFY.NS", "INOXWIND.NS", "INTELLECT.NS", "INDIGO.NS", 
    "IPCALAB.NS", "ITC.NS", "ITDC.NS", "JBCHEPHARM.NS", "JKCEMENT.NS", "JKLAKSHMI.NS", "JKPAPER.NS", "JMFINANCIL.NS", "JSWENERGY.NS", "JSWINFRA.NS", 
    "JSWSTEEL.NS", "JWL.NS", "J&KBANK.NS", "JINDALSAW.NS", "JINDALSTEL.NS", "JIOFIN.NS", "JUBLFOOD.NS", "JUBLINGREA.NS", "JUBLPHARMA.NS", "JUSTDIAL.NS", 
    "JYOTHYLAB.NS", "KNRCON.NS", "KPITTECH.NS", "KRBL.NS", "KSB.NS", "KAJARIACER.NS", "KPIL.NS", "KALYANKJIL.NS", "KANSAINER.NS", "KARURVYSYA.NS", 
    "KEC.NS", "KEI.NS", "KOTAKBANK.NS", "KIMS.NS", "KROSS.NS", "KIRLOSENG.NS", "KIRLOSIND.NS", "L&TFH.NS", "LTTS.NS", "LICHSGFIN.NS", 
    "LTIM.NS", "LT.NS", "LATENTVIEW.NS", "LAURUSLABS.NS", "LXCHEM.NS", "LEMONTREE.NS", "LICI.NS", "LINDEINDIA.NS", "LLOYDSME.NS", "LUPIN.NS", 
    "LUXIND.NS", "MMTC.NS", "MOIL.NS", "MRF.NS", "MTARTECH.NS", "M&M.NS", "M&MFIN.NS", "MAHLOG.NS", "MANAPPURAM.NS", "MANGCHEFER.NS", 
    "MRPL.NS", "MANKIND.NS", "MARICO.NS", "MARUTI.NS", "MASTEK.NS", "MAZDOCK.NS", "MEDANTA.NS", "METROBRAND.NS", "METROPOLIS.NS", "MFSL.NS", 
    "MAXHEALTH.NS", "MAZDA.NS", "MHRIL.NS", "MIDHANI.NS", "MINDACORP.NS", "MSUMI.NS", "MOTILALOFS.NS", "MPHASIS.NS", "MCX.NS", "MUTHOOTFIN.NS", 
    "NATCOPHARM.NS", "NBCC.NS", "NCC.NS", "NESCO.NS", "NHPC.NS", "NLCINDIA.NS", "NMDC.NS", "NTPC.NS", "NH.NS", "NATIONALUM.NS", 
    "NAVINFLUOR.NS", "NAZARA.NS", "NEOGEN.NS", "NESTLEIND.NS", "NETWEB.NS", "NETWORK18.NS", "NIGHTINGALE.NS", "NIPON_IND.NS", "NLCINDIA.NS", "NOCIL.NS", 
    "NUVAMA.NS", "NUVOCO.NS", "OBEROIRLTY.NS", "ONGC.NS", "OIL.NS", "OLECTRA.NS", "PAYTM.NS", "OFSS.NS", "ORIENTELEC.NS", "PCBL.NS", 
    "PIIND.NS", "PNBHOUSING.NS", "PNCINFRA.NS", "PVRINOX.NS", "PAGEIND.NS", "PANTALOON.NS", "PATANJALI.NS", "PERSISTENT.NS", "PETRONET.NS", "PHOENIXLTD.NS", 
    "PIDILITIND.NS", "PEL.NS", "PPLPHARMA.NS", "POLYMED.NS", "POLYCAB.NS", "POONAWALLA.NS", "PFC.NS", "POWERGRID.NS", "PRAJIND.NS", "PRESTIGE.NS", 
    "PRINCEPIPE.NS", "PRUDENT.NS", "PRSMJOHNSN.NS", "QUESS.NS", "RECLTD.NS", "RHIM.NS", "RITES.NS", "RKFORGE.NS", "RVNL.NS", "RCF.NS", 
    "RELIANCE.NS", "RBA.NS", "ROSSARI.NS", "ROUTE.NS", "SBICARD.NS", "SBILIFE.NS", "SJVN.NS", "SKFINDIA.NS", "SRF.NS", "SAFARI.NS", 
    "SAMHI.NS", "SANOFI.NS", "SAPPHIRE.NS", "SAREGM.NS", "SBIN.NS", "SHARDAMOTR.NS", "SHOPERSTOP.NS", "SHREECEM.NS", "SHRIRAMFIN.NS", "SIEMENS.NS", 
    "SIGNATURE.NS", "SOBHA.NS", "SOLARINDS.NS", "SONACOMS.NS", "SONATSOFTW.NS", "SPARC.NS", "STERTOOLS.NS", "STARHEALTH.NS", "STLTECH.NS", "SUMICHEM.NS", 
    "SPANDANA.NS", "SPAL.NS", "SUNPHARMA.NS", "SUNTV.NS", "SUNDARMFIN.NS", "SUNDRMFAST.NS", "SUNTECK.NS", "SUPRAJIT.NS", "SUPREMEIND.NS", "SUZLON.NS", 
    "SYNGENE.NS", "TATACOMM.NS", "TATACONSUM.NS", "TATAELXSI.NS", "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TATATECH.NS", "TCS.NS", "TECHM.NS", 
    "TEJASNET.NS", "THERMAX.NS", "TIMKEN.NS", "TITAN.NS", "TORNTPHARM.NS", "TORNTPOWER.NS", "TRENT.NS", "TRIDENT.NS", "TRITURBINE.NS", "TIINDIA.NS", 
    "UCOBANK.NS", "UNOMINDA.NS", "UPL.NS", "UTIAMC.NS", "ULTRACEMCO.NS", "UNIONBANK.NS", "USHAMART.NS", "VGUARD.NS", "VIBHOR.NS", "VIPIND.NS", 
    "VAIBHAVGBL.NS", "VAKRANGEE.NS", "VALIANTORG.NS", "VARDHMAN.NS", "VARROC.NS", "VBL.NS", "VEDL.NS", "VENKEYS.NS", "VINATIORGA.NS", "VOLTAS.NS", 
    "WELCORP.NS", "WELSPUNLIV.NS", "WESTLIFE.NS", "WHIRLPOOL.NS", "WIPRO.NS", "YESBANK.NS", "ZEEENT.NS", "ZENSARTECH.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"]

def check_hammer_perfect(ticker):
    try:
        # डेटा डाऊनलोड करताना 'auto_adjust=False' ठेवणे गरजेचे आहे जेणेकरून 'Open' बदलणार नाही
        df = yf.download(ticker, period=period_map[selected_tf], interval=tf_map[selected_tf], progress=False, auto_adjust=False)
        
        if df.empty or len(df) < 2:
            return None
        
        # शेवटची पूर्ण झालेली कॅन्डल (Current Bar)
        last = df.iloc[-1]
        o = float(last['Open'])
        h = float(last['High'])
        l = float(last['Low'])
        c = float(last['Close'])
        
        # --- तुमची इमेजमधील तंतोतंत कंडिशन ---
        
        body = abs(c - o)
        if body == 0: body = 0.01 # Division error टाळण्यासाठी
        
        # १. (Open - Low) >= (Close - Open) * 2 [इमेजमधील पहिली ओळ]
        cond1 = (o - l) >= (body * multiplier)
        
        # २. (High - Close) <= (High - Low) * 0.25 [इमेजमधील दुसरी ओळ]
        cond2 = (h - max(o, c)) <= ((h - l) * 0.25)
        
        # ३. Close > Open [इमेजमधील तिसरी ओळ - Bullish Hammer]
        cond3 = c > o
        
        # ४. Close > 500 [इमेजमधील चौथी ओळ]
        cond4 = c > 500
        
        # सर्व अटी पूर्ण झाल्या तरच रिझल्ट दाखवा
        if cond1 and cond2 and cond3 and cond4:
            return {
                "Stock Symbol": ticker,
                "LTP": round(c, 2),
                "Open": round(o, 2),
                "High": round(h, 2),
                "Low": round(l, 2),
                "View Chart": f"https://www.tradingview.com/chart/?symbol=NSE:{ticker.replace('.NS','')}"
            }
        return None
    except:
        return None

if st.button("🚀 अचूक स्कॅन सुरू करा"):
    st.info(f"स्कॅनिंग सुरू झाले आहे. {selected_tf} डेटा तपासला जात आहे...")
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        results = list(executor.map(check_hammer_perfect, tickers))
    
    found = [res for res in results if res is not None]
    
    if found:
        st.success(f"सापडले! {len(found)} स्टॉक्स तुमच्या अटीत बसले आहेत.")
        df_final = pd.DataFrame(found)
        st.data_editor(
            df_final,
            column_config={"View Chart": st.column_config.LinkColumn()},
            hide_index=True
        )
    else:
        st.warning(f"सध्या {selected_tf} मध्ये या अटीत कोणताही स्टॉक बसत नाही. (जर RKFORGE चार्टवर हॅमर दिसत असेल, तर टाइमफ्रेम तपासा).")
