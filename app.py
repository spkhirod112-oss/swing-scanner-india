from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Swing Scanner India",page_icon="📈",layout="wide")
BASE=Path(__file__).parent
st.title("📈 Swing Scanner India")
st.caption("NSE / BSE • End-of-day research • Free unofficial data • Not live exchange quotes")
st.warning("Educational watchlist only. Prices may be delayed, stale, missing or unadjusted for some corporate events. Verify on an exchange or broker before any decision.")
statusfile=BASE/"data/status.json"
file=BASE/"data/watchlist.csv"
if not statusfile.exists() or not file.exists():
    st.error("No downloaded market data yet. The scheduled fetch must complete successfully.")
    st.code("python fetch.py")
    st.stop()
status=json.loads(statusfile.read_text())
st.caption(f"Data source: {status.get('provider','Unknown')} | Last fetch attempt (UTC): {status.get('updated_utc','Unknown')} | Coverage: {status.get('processed',0)}/{status.get('universe',0)}")
try:
    updated=datetime.fromisoformat(status["updated_utc"])
    age=(datetime.now(timezone.utc)-updated).total_seconds()/3600
    if age>72: st.error(f"STALE: last fetch was {age/24:.1f} days ago.")
except (ValueError,KeyError):
    st.error("Fetch timestamp unavailable.")
if status.get("status")!="ok":
    st.error("Data incomplete: benchmark or symbol retrieval failed. Relative-strength results may be unavailable.")
if status.get("errors"):
    with st.expander(f"Download issues ({len(status['errors'])})"):
        st.write(status["errors"])
df=pd.read_csv(file)
if df.empty: st.info("No valid symbols"); st.stop()
latest=max(pd.to_datetime(df["Date"]))
if (datetime.now().date()-latest.date()).days>5:
    st.error(f"Price history is stale: latest candle {latest.date()}")
ex=st.multiselect("Exchange",["NSE","BSE"],default=["NSE","BSE"])
qualified_only=st.toggle("Show fully qualified only",value=False)
min_checks=st.slider("Minimum filters passed",0,6,4)
filtered=df[df["Exchange"].isin(ex)&(df["Checks"]>=min_checks)]
if qualified_only:
    filtered=filtered[filtered["Qualified"].astype(str).str.lower()=="true"]
st.metric("Matching candidates",len(filtered))
columns=["Symbol","Exchange","Date","Close","RSI","Checks","Distance to resistance %",
         "Entry trigger","Invalidation","20d return %","Avg traded ₹Cr","Checks detail"]
st.dataframe(filtered[columns],hide_index=True,use_container_width=True)
st.download_button("Download watchlist CSV",filtered.to_csv(index=False).encode(),
                   file_name="swing_watchlist.csv",mime="text/csv")
if len(filtered):
    ticker=st.selectbox("Inspect chart",filtered["Ticker"].tolist())
    histfile=BASE/"data"/(ticker.replace(".","_")+".csv")
    if histfile.exists():
        h=pd.read_csv(histfile).tail(120)
        fig=go.Figure()
        fig.add_trace(go.Candlestick(x=h["Date"],open=h["Open"],high=h["High"],
                                     low=h["Low"],close=h["Close"],name=ticker))
        fig.add_trace(go.Scatter(x=h["Date"],y=h["Close"].rolling(50).mean(),
                                 name="50-session average"))
        fig.update_layout(height=410,xaxis_rangeslider_visible=False,
                          margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig,use_container_width=True)
st.caption("Entry triggers and invalidation are illustrative price levels, not orders. Brokerage, taxes, slippage, liquidity and corporate actions are not modeled. Free Yahoo Finance coverage is not guaranteed for all NSE/BSE listings.")
