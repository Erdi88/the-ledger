"""Point-in-time annual fundamentals from SEC EDGAR 'companyfacts' (US filers only).

Each value carries the date it was FILED, so a feature at date t only uses what was public at t.
"""
import json, time, urllib.request
import pandas as pd
from .config import DATA, contact

TAGS = {
    'revenue': ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'SalesRevenueNet'],
    'net_income': ['NetIncomeLoss'],
    'ocf': ['NetCashProvidedByUsedInOperatingActivities'],
    'capex': ['PaymentsToAcquirePropertyPlantAndEquipment'],
    'equity': ['StockholdersEquity'],
    'debt': ['LongTermDebt', 'LongTermDebtNoncurrent'],
    'shares': ['WeightedAverageNumberOfDilutedSharesOutstanding', 'WeightedAverageNumberOfSharesOutstandingBasic'],
    'eps': ['EarningsPerShareDiluted', 'EarningsPerShareBasic'],
    'dps': ['CommonStockDividendsPerShareDeclared', 'CommonStockDividendsPerShareCashPaid'],
    'buyback': ['PaymentsForRepurchaseOfCommonStock'],
}
STOCK_ITEMS = {'equity', 'debt'}   # balance-sheet values have no duration

def _get(url):
    req = urllib.request.Request(url, headers={'User-Agent': f'the-ledger-research-bot {contact()}'})
    with urllib.request.urlopen(req, timeout=40) as f:
        return json.load(f)

def cik_map():
    data = _get('https://www.sec.gov/files/company_tickers.json')
    return {v['ticker'].upper(): int(v['cik_str']) for v in data.values()}

def annual_records(facts):
    """Return DataFrame(end, filed, <metrics>) of fiscal-year values, original filing per period."""
    gaap = facts.get('facts', {}).get('us-gaap', {})
    by_end = {}
    for metric, tags in TAGS.items():
        for tag in tags:
            node = gaap.get(tag)
            if not node: continue
            got = False
            for unit, rows in node['units'].items():
                for r in rows:
                    if r.get('form') not in ('10-K', '10-K/A') or r.get('fp') != 'FY': continue
                    if metric not in STOCK_ITEMS and 'start' in r:
                        days = (pd.Timestamp(r['end']) - pd.Timestamp(r['start'])).days
                        if not 340 <= days <= 390: continue
                    key = r['end']
                    cur = by_end.setdefault(key, {'end': key, 'filed': r['filed']})
                    if r['filed'] < cur['filed']: cur['filed'] = r['filed']   # earliest disclosure of this period
                    cur.setdefault(metric, r['val']); got = True
            if got: break
    if not by_end: return None
    df = pd.DataFrame(sorted(by_end.values(), key=lambda x: x['end']))
    df['end'] = pd.to_datetime(df['end']); df['filed'] = pd.to_datetime(df['filed'])
    return df

def update(tickers, pause=0.3):
    (DATA / 'fundamentals').mkdir(parents=True, exist_ok=True)
    ciks = cik_map(); status = {}
    for t in tickers:
        cik = ciks.get(t.upper().replace('-', '-')) or ciks.get(t.upper().replace('-', '.'))
        if not cik: status[t] = {'ok': False, 'error': 'no CIK'}; continue
        try:
            df = annual_records(_get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json'))
            if df is None: status[t] = {'ok': False, 'error': 'no annual facts'}; continue
            df.to_csv(DATA / 'fundamentals' / f'{t}.csv', index=False)
            status[t] = {'ok': True, 'years': len(df), 'last_filed': str(df['filed'].max().date())}
        except Exception as e:
            status[t] = {'ok': False, 'error': str(e)[:200]}
        time.sleep(pause)
    return status

def load(t):
    p = DATA / 'fundamentals' / f'{t}.csv'
    if not p.exists(): return None
    return pd.read_csv(p, parse_dates=['end', 'filed']).sort_values('filed')
