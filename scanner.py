"""Educational, end-of-day research screener. No trading execution."""
import pandas as pd
import numpy as np

def calculate(df, benchmark_return=None):
    d=df.sort_values("Date").copy().reset_index(drop=True)
    if len(d)<65: return None
    close=d["Close"].astype(float)
    high=d["High"].astype(float)
    low=d["Low"].astype(float)
    volume=d["Volume"].astype(float)
    if (close<=0).any() or (volume<0).any(): return None
    delta=close.diff()
    up=delta.clip(lower=0).ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    down=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False,min_periods=14).mean()
    rs=up/down.replace(0,np.nan)
    rsi_series=(100-100/(1+rs)).where(down.ne(0),100).where(up.ne(0),0)
    rsi=rsi_series.iloc[-1]
    sma50=close.rolling(50).mean().iloc[-1]
    resistance=high.shift(1).rolling(20).max().iloc[-1]
    support=low.tail(10).min()
    consolidation=(high.tail(10).max()/low.tail(10).min()-1)*100
    traded=(close*volume).tail(20).mean()
    ret20=(close.iloc[-1]/close.iloc[-21]-1)*100
    distance=(resistance-close.iloc[-1])/resistance*100
    volume_ratio=volume.tail(5).mean()/max(volume.tail(20).mean(),1)
    latest=close.iloc[-1]
    checks={
      "Uptrend": latest>sma50,
      "RSI 50–65": pd.notna(rsi) and 50<=rsi<=65,
      "Consolidation <8%": consolidation<8,
      "Near resistance": 0<=distance<=5,
      "Liquid >₹5Cr/day": traded>=5e7,
      "Relative strength": benchmark_return is not None and ret20>benchmark_return,
    }
    if pd.isna(rsi) or pd.isna(resistance): return None
    passed=sum(bool(x) for x in checks.values())
    return {
       "Date":str(pd.to_datetime(d["Date"].iloc[-1]).date()),
       "Close":round(latest,2),"RSI":round(float(rsi),1),
       "SMA50":round(float(sma50),2),
       "Resistance":round(float(resistance),2),
       "Support":round(float(support),2),
       "Entry trigger":round(float(resistance)*1.002,2),
       "Invalidation":round(float(support),2),
       "20d return %":round(float(ret20),2),
       "Distance to resistance %":round(float(distance),2),
       "10d range %":round(float(consolidation),2),
       "Volume ratio":round(float(volume_ratio),2),
       "Avg traded ₹Cr":round(float(traded)/1e7,2),
       "Checks":passed,"Qualified":all(checks.values()),
       "Checks detail":", ".join(k for k,v in checks.items() if not v)
    }
