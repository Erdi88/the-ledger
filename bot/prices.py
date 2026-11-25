"""Daily adjusted prices from Yahoo Finance's public chart endpoint (unofficial; personal research use)."""
import csv, datetime as dt, json, time, urllib.parse, urllib.request
import pandas as pd
from .config import DATA

def _safe(t): return t.replace('^', '_').replace('=', '_').replace('/', '_')
def path(t): return DATA / 'prices' / f'{_safe(t)}.csv'

def parse_chart(payload):
    r = payload['chart']['result'][0]
    ts = r.get('timestamp') or []
    q = r['indicators']['quote'][0]
    adj = (r['indicators'].get('adjclose') or [{}])[0].get('adjclose') or q['close']
    rows = []
    for i, t in enumerate(ts):
        c, a = q['close'][i], adj[i]
        if c is None or a is None: continue
        day = dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat()
        rows.append((day, round(c, 6), round(a, 6), q['volume'][i] or 0))
    # Yahoo can repeat the last day (intraday bar); keep the last row per date.
    return list(dict(((d, (d, c, a, v)) for d, c, a, v in rows)).values())

def fetch(t, retries=3):
    url = 'https://query1.finance.yahoo.com/v8/finance/chart/' + urllib.parse.quote(t) + f'?period1=0&period2={int(time.time()) + 86400}&interval=1d&events=div%2Csplits'
    for n in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (the-ledger research bot)'})
            with urllib.request.urlopen(req, timeout=30) as f:
                return parse_chart(json.load(f))
        except Exception as e:
            err = e; time.sleep(2 * (n + 1))
    raise RuntimeError(f'price fetch failed for {t}: {err}')

def update(tickers, pause=0.4):
    DATA.joinpath('prices').mkdir(parents=True, exist_ok=True)
    status = {}
    for t in tickers:
        try:
            rows = fetch(t)
            with open(path(t), 'w', newline='') as f:
                w = csv.writer(f); w.writerow(['date', 'close', 'adjclose', 'volume']); w.writerows(rows)
            status[t] = {'ok': True, 'rows': len(rows), 'last': rows[-1][0]}
        except Exception as e:
            status[t] = {'ok': False, 'error': str(e)[:200]}
        time.sleep(pause)
    return status

def load(t):
    p = path(t)
    if not p.exists(): return None
    df = pd.read_csv(p, parse_dates=['date']).set_index('date')
    return df['adjclose'].astype(float)
