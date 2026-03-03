import streamlit as st
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# १. पेज सेटिंग
st.set_page_config(page_title="Nifty 500 Pro Screener", page_icon="⚡", layout="wide")
st.title("⚡ Nifty 500 Fast Hammer Screener")

# २. साइडबार - सेटिंग्स
st.sidebar.header("Screener Settings")
multiplier = st.sidebar.number_input("Shadow Multiplier टाका", min_value=1.0, max_value=10.0, value=2.5, step=0.1)

timeframe_map = {
    "1 Hour": {"interval": "60m", "period": "2y"},
    "2 Hours": {"interval": "120m", "period": "2y"},
    "3 Hours": {"interval": "180m", "period": "2y"},
    "4 Hours": {"interval": "240m", "period": "2y"},
    "1 Day": {"interval": "1d", "period": "5y"},
    "1 Week": {"interval": "1wk", "period": "max"},
    "1 Month": {"interval": "1mo", "period": "max"}
}
selected_tf = st.sidebar.selectbox("Timeframe निवडा", list(timeframe_map.keys()))

# ३. Nifty 500 पूर्ण लिस्ट (yfinance .NS सह)
nifty_500_tickers = [
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
    "ELGIEQUIP.NS", "EMAMILTD.NS", "ENDURANCE.NS", "ENGINERSIN.NS", "ESCORTS.NS", "EXIDEIND.NS", "FSL.NS", "FSNREMS.NS", "FEDERALBNK.NS", 
    "FACT.NS", "FINEORG.NS", "FINCABLES.NS", "FINPIPE.NS", "FLUOROCHEM.NS", "FORTIS.NS", "GRINFRA.NS", "GAIL.NS", "GMRINFRA.NS", 
    "GNA.NS", "GOCLCORP.NS", "GPIL.NS", "GRSE.NS", "GARDENREACH.NS", "GEPIL.NS", "GESHIP.NS", "GENUSPOWER.NS", "GLAND.NS", 
    "GLAXO.NS", "GLENMARK.NS", "GMM_PFAUDL.NS", "GOCOLORS.NS", "GODFRYPHLP.NS", "GODREJAGRO.NS", "GODREJCP.NS", "GODREJIND.NS", "GODREJPROP.NS", "GRANULES.NS", 
    "GRAPHITE.NS", "GRASIM.NS", "GRAVITA.NS", "GREAVESCOT.NS", "GRINDWELL.NS", "GUJALKALI.NS", "GUJGASLTD.NS", "GNFC.NS", "GPPL.NS", "GSFC.NS", 
    "GSPL.NS", "GULFOILLUB.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HMT.NS", "HFCL.NS", "HAPPSTMNDS.NS", "HAVELLS.NS", "HEROMOTOCO.NS", 
    "HINDALCO.NS", "HAL.NS", "HINDCOPPER.NS", "HINDPETRO.NS", "HINDUNILVR.NS", "HINDZINC.NS", "HOMEFIRST.NS", "HONAUT.NS", "HUDCO.NS", "ICICIBANK.NS", 
    "ICICIGI.NS", "ICICIPRULI.NS", "ISEC.NS", "IDBI.NS", "IDFCFIRSTB.NS", "IDFC.NS", "IFCI.NS", "IIFL.NS", "IRB.NS", "IRCON.NS", 
    "IRCTC.NS", "IRFC.NS", "ITI.NS", "INDIA_GLYCO.NS", "INDIACEM.NS", "IBREALEST.NS", "INDIAMART.NS", "INDIANB.NS", "IEX.NS", "INDHOTEL.NS", 
    "IOC.NS", "IOB.NS", "INDUSINDBK.NS", "INDUSTOWER.NS", "INFIBEAM.NS", "INFY.NS", "INOXWIND.NS", "INTELLECT.NS", "INDIGO.NS", 
    "IPCALAB.NS", "ITC.NS", "ITDC.NS", "JBCHEPHARM.NS", "JKCEMENT.NS", "JKLAKSHMI.NS", "JKPAPER.NS", "JMFINANCIL.NS", "JSWENERGY.NS", "JSWINFRA.NS", 
    "JSWSTEEL.NS", "JWL.NS", "J&KBANK.NS", "JINDALSAW.NS", "JINDALSTEL.NS", "JIOFIN.NS", "JUBLFOOD.NS", "JUBLINGREA.NS", "JUBLPHARMA.NS", "JUSTDIAL.NS", 
    "JYOTHYLAB.NS", "KNRCON.NS", "KPITTECH.NS", "KRBL.NS", "KSB.NS", "KAJARIACER.NS", "KPIL.NS", "KALYANKJIL.NS", "KANSAINER.NS", "KARURVYSYA.NS", 
    "KEC.NS", "KEI.NS", "KOTAKBANK.NS", "KIMS.NS", "KROSS.NS", "KIRLOSENG.NS", "KIRLOSIND.NS", "L&TFH.NS", "LTTS.NS", "LICHSGFIN.NS", 
    "LTIM.NS", "LT.NS", "LATENTVIEW.NS", "LAURUSLABS.NS", "LXCHEM.NS", "LEMONTREE.NS", "LICI.NS", "LINDEINDIA.NS", "LLOYDSME.NS", "LUPIN.NS", 
    "LUXIND.NS", "MMTC.NS", "MOIL.NS", "MRF.NS", "MTARTECH.NS", "M&M.NS", "M&MFIN.NS", "MAHLOG.NS", "MANAPPURAM.NS", "MANGCHEFER.NS", 
    "MRPL.NS", "MANKIND.NS", "MARICO.NS", "MARUTI.NS", "MASTEK.NS", "MAZDOCK.NS", "MEDANTA.NS", "METROBRAND.NS", "METROPOLIS.NS", "MFSL.NS", 
    "MAXHEALTH.NS", "MAZDA.NS", "MHRIL.NS", "MIDHANI.NS", "MINDACORP.NS", "MSUMI.NS", "MOTILALOFS.NS", "MPHASIS.NS", "MCX.NS", "MUTHOOTFIN.NS", 
    "NATCOPHARM.NS", "NBCC.NS", "NCC.NS", "NESCO.NS", "NHPC.NS", "NLCINDIA.NS", "NMDC.NS", "NTPC.NS", "NH.NS", "NATIONALUM.NS", 
    "NAVINFLUOR.NS", "NAZARA.NS", "NEOGEN.NS", "NESTLEIND.NS", "NETWEB.NS", "NETWORK18.NS", "NIGHTINGALE.NS", "NIPON_IND.NS", "NOCIL.NS", 
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
    "WELCORP.NS", "WELSPUNLIV.NS", "WESTLIFE.NS", "WHIRLPOOL.NS", "WIPRO.NS", "YESBANK.NS", "ZEEENT.NS", "ZENSARTECH.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"
]

# ४. Hammer Check Function
def check_hammer(ticker):
    try:
        settings = timeframe_map[selected_tf]
        df = yf.download(ticker, period=settings['period'], interval=settings['interval'], progress=False)
        if df.empty or len(df) < 1: return None
        
        last = df.iloc[-1]
        o, c, h, l = float(last['Open']), float(last['Close']), float(last['High']), float(last['Low'])
        body = abs(c - o)
        lower_shadow = min(o, c) - l
        upper_shadow = h - max(o, c)
        
        if body == 0: body = 0.01
        
        if lower_shadow > (body * multiplier) and upper_shadow < (body * 0.5):
            # TradingView URL तयार करणे
            clean_ticker = ticker.replace(".NS", "")
            tv_url = f"https://www.tradingview.com/chart/?symbol=NSE:{clean_ticker}"
            return {"Stock": ticker, "Price": round(c, 2), "View Chart": tv_url}
        return None
    except:
        return None

# ५. स्कॅनिंग आणि रिझल्ट
if st.button(f"🚀 {selected_tf} साठी निफ्टी ५०० स्कॅन करा"):
    st.info(f"स्कॅनिंग सुरू झाले आहे (५०० स्टॉक्स)... कृपया ६० सेकंद थांबा.")
    
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(check_hammer, nifty_500_tickers))
    
    found_stocks = [res for res in results if res is not None]
    
    if found_stocks:
        st.success(f"सापडले! {len(found_stocks)} स्टॉक्समध्ये Hammer दिसली.")
        
        # टेबलमध्ये क्लिक करण्यायोग्य लिंक दाखवण्यासाठी
        df_result = pd.DataFrame(found_stocks)
        
        # Streamlit मध्ये लिंक कॉलम बनवणे
        st.data_editor(
            df_result,
            column_config={
                "View Chart": st.column_config.LinkColumn("TradingView चार्ट")
            },
            hide_index=True,
        )
    else:
        st.warning("या निकषात सध्या कोणताही स्टॉक बसत नाही.")

st.divider()
st.caption("Disclaimer: हाय-स्पीड थ्रेडिंगमुळे कधीकधी yfinance कडून रिस्पॉन्स येण्यास वेळ लागू शकतो.")
