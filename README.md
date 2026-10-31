# Swing Scanner India (educational prototype)

Mobile-friendly Streamlit app with an automated daily refresh workflow and a small, editable NSE/BSE stock universe.

## Important limitations
- **Not connected directly to NSE/BSE**. Uses unofficial Yahoo Finance via `yfinance` (`.NS` and `.BO`) as a zero-cost *prototype* source.
- Daily data can be delayed, inaccurate, blocked or missing. Do not interpret a successful GitHub run as guaranteed data freshness.
- Only symbols in `symbols.csv` are screened; this is **not an exhaustive NSE/BSE market scan**.
- No brokerage connection, trades, buy/sell automation, or guaranteed returns.
- Stock splits/corporate actions and liquidity need independent verification.
- GitHub Actions scheduled jobs can run late or be disabled after repository inactivity.
- Streamlit Community Cloud apps can sleep; open the app to wake it.

## Deploy from Android or desktop
1. Connect GitHub to ChatGPT if supported, or create a GitHub repository.
2. Upload the contents of this ZIP to the repository **preserving `.github/workflows/update.yml`**.
3. In GitHub Actions, manually run `Update end-of-day watchlist` once. Ensure workflow permissions permit writing to the repository.
4. Wait for the action to create `data/watchlist.csv` and `data/status.json`.
5. Sign into https://share.streamlit.io with GitHub, select the repository and `app.py`, and deploy.
6. Open the resulting `*.streamlit.app` address on your phone. Add it to the home screen.
7. Edit `symbols.csv` to expand the tracked stock universe. Larger universes increase rate-limit risk.

## Run locally
```bash
pip install -r requirements.txt
python fetch.py
streamlit run app.py
```

## Screening
Trend: close above SMA50; RSI(14): 50–65; 10-session high-low range <8%; within 5% below prior 20-session high; 20-session mean daily traded value >₹5 crore; 20-session return exceeds Nifty 50 (when benchmark is available). All six checks required for `Qualified`.

These rules are illustrative, not backtested or personalized advice.
