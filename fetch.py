"""Fetch free, unofficial, potentially delayed Yahoo Finance daily candles."""
from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd
import yfinance as yf
from scanner import calculate

BASE=Path(__file__).parent
DATA=BASE/"data"
DATA.mkdir(exist_ok=True)

def download(ticker):
    x=yf.download(ticker,period="1y",interval="1d",auto_adjust=True,
                  progress=False,threads=False,timeout=20)
    if x is None or x.empty: return None
    if isinstance(x.columns,pd.MultiIndex):
        x.columns=x.columns.get_level_values(0)
    x=x.reset_index()
    if "Date" not in x: return None
    x["Date"]=pd.to_datetime(x["Date"]).dt.tz_localize(None)
    return x[["Date","Open","High","Low","Close","Volume"]].dropna()

def run():
    symbols=pd.read_csv(BASE/"symbols.csv",dtype=str).fillna("")
    errors=[]
    benchmark=download("^NSEI")
    benchmark_return=None
    if benchmark is not None and len(benchmark)>=21:
        benchmark_return=(benchmark["Close"].iloc[-1]/benchmark["Close"].iloc[-21]-1)*100
    results=[]
    for _,item in symbols.iterrows():
        symbol=item["symbol"].strip()
        exchange=item["exchange"].strip().upper()
        if exchange not in ("NSE","BSE") or not symbol: continue
        ticker=symbol+(".NS" if exchange=="NSE" else ".BO")
        try:
            history=download(ticker)
            if history is None:
                errors.append(f"{ticker}: no data")
                continue
            out=calculate(history,benchmark_return)
            if out is None:
                errors.append(f"{ticker}: insufficient history")
                continue
            out.update({"Symbol":symbol,"Exchange":exchange,"Ticker":ticker})
            results.append(out)
            history.to_csv(DATA/(ticker.replace(".","_")+".csv"),index=False)
        except Exception as exc:
            errors.append(f"{ticker}: {type(exc).__name__}")
    # Never erase last good watchlist on a total provider failure
    if results:
        pd.DataFrame(results).sort_values(
            ["Qualified","Checks","Distance to resistance %"],
            ascending=[False,False,True]
        ).to_csv(DATA/"watchlist.csv",index=False)
    metadata={
        "updated_utc":datetime.now(timezone.utc).isoformat(),
        "provider":"Yahoo Finance via yfinance (unofficial, delayed)",
        "universe":len(symbols),"processed":len(results),
        "benchmark_available":benchmark_return is not None,
        "errors":errors,
        "status":"ok" if results and benchmark_return is not None else "partial_or_failed"
    }
    (DATA/"status.json").write_text(json.dumps(metadata,indent=2))
    print(json.dumps(metadata,indent=2))

if __name__=="__main__":
    run()
