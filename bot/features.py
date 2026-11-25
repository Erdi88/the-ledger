"""Feature panel. Every value at date t uses only information available at t (no look-ahead)."""
import numpy as np
import pandas as pd
from . import prices, sec
from .config import HORIZONS, SAMPLE_EVERY, universe

PRICE_FEATURES = ['mom_21', 'mom_63', 'mom_126', 'mom_252_skip21', 'vol_63', 'dd_252', 'ma_gap_200', 'rel_63']
MACRO_FEATURES = ['vix', 'vix_chg_21', 'tnx', 'tnx_chg_63', 'usdnok_chg_63', 'brent_chg_63', 'mkt_mom_63', 'mkt_dd_252']
# Graham (value, safety), Munger (quality, avoid stupidity), Thorndike's outsiders (capital allocation, FCF/share).
FUND_FEATURES = ['earn_yield', 'pb', 'fcf_yield', 'roe', 'debt_to_equity', 'net_margin', 'eps_growth',
                 'share_change', 'buyback_yield', 'div_yield', 'profit_years']
FEATURES = PRICE_FEATURES + MACRO_FEATURES + FUND_FEATURES + ['is_no']

def _dd(s, n=252): return s / s.rolling(n, min_periods=60).max() - 1

def price_features(s, bench):
    r = np.log(s).diff()
    f = pd.DataFrame(index=s.index)
    f['mom_21'] = s / s.shift(21) - 1
    f['mom_63'] = s / s.shift(63) - 1
    f['mom_126'] = s / s.shift(126) - 1
    f['mom_252_skip21'] = s.shift(21) / s.shift(252) - 1
    f['vol_63'] = r.rolling(63).std() * np.sqrt(252)
    f['dd_252'] = _dd(s)
    f['ma_gap_200'] = s / s.rolling(200, min_periods=150).mean() - 1
    b = bench.reindex(s.index).ffill()
    f['rel_63'] = f['mom_63'] - (b / b.shift(63) - 1)
    return f

def macro_frame(index, series):
    m = pd.DataFrame(index=index)
    def al(k):
        if k not in series: return pd.Series(np.nan, index=index)
        s = series[k]; s = s[~s.index.duplicated(keep='last')]
        return s.reindex(index.union(s.index)).ffill().reindex(index)
    vix, tnx, fx, brent, spx = al('vix'), al('tnx'), al('usdnok'), al('brent'), al('spx')
    m['vix'] = vix; m['vix_chg_21'] = vix / vix.shift(21) - 1
    m['tnx'] = tnx; m['tnx_chg_63'] = tnx - tnx.shift(63)
    m['usdnok_chg_63'] = fx / fx.shift(63) - 1
    m['brent_chg_63'] = brent / brent.shift(63) - 1
    m['mkt_mom_63'] = spx / spx.shift(63) - 1
    m['mkt_dd_252'] = _dd(spx)
    return m

def fundamental_features(s, fund):
    """As-of join on FILING date; yields use the price on the day (so they move daily like Mr. Market)."""
    out = pd.DataFrame(np.nan, index=s.index, columns=FUND_FEATURES)
    if fund is None or fund.empty: return out
    f = fund.copy().reset_index(drop=True)
    nan = pd.Series(np.nan, index=f.index)
    g = lambda k: f[k] if k in f else nan
    sh = g('shares')
    f['bvps'] = g('equity') / sh
    f['eps_v'] = g('eps') if 'eps' in f else g('net_income') / sh
    f['fcf_ps'] = (g('ocf') - g('capex').fillna(0)) / sh
    f['roe_v'] = g('net_income') / g('equity')
    f['d2e'] = g('debt').fillna(0) / g('equity')
    f['nm'] = g('net_income') / g('revenue')
    f['epsg'] = f['eps_v'].pct_change(fill_method=None)
    f['shg'] = sh.pct_change(fill_method=None)
    f['bb'] = g('buyback') / sh
    f['dps_v'] = g('dps')
    f['py'] = (g('net_income') > 0).astype(float).where(g('net_income').notna()).rolling(5, min_periods=1).sum()
    cols = ['bvps', 'eps_v', 'fcf_ps', 'roe_v', 'd2e', 'nm', 'epsg', 'shg', 'bb', 'dps_v', 'py']
    keep = f[['filed'] + cols].sort_values('filed')
    base = pd.DataFrame({'date': s.index, 'px': s.values})
    m = pd.merge_asof(base, keep, left_on='date', right_on='filed', direction='backward')
    # Fundamentals older than ~18 months are stale: treat as unknown rather than pretend they are current.
    m.loc[(m['date'] - m['filed']).dt.days > 550, cols] = np.nan
    px = m['px']
    out['earn_yield'] = (m['eps_v'] / px).values
    out['pb'] = (px / m['bvps']).where(m['bvps'] > 0).values
    out['fcf_yield'] = (m['fcf_ps'] / px).values
    out['roe'] = m['roe_v'].values; out['debt_to_equity'] = m['d2e'].values; out['net_margin'] = m['nm'].values
    out['eps_growth'] = m['epsg'].clip(-2, 2).values; out['share_change'] = m['shg'].values
    out['buyback_yield'] = (m['bb'] / px).values; out['div_yield'] = (m['dps_v'] / px).values
    out['profit_years'] = m['py'].values
    return out

def load_all():
    u = universe()
    px = {x['t']: prices.load(x['t']) for x in u['stocks']}
    px = {k: v for k, v in px.items() if v is not None and len(v) > 300}
    bench = {r: prices.load(t) for r, t in u['benchmarks'].items()}
    macro = {'vix': prices.load(u['macro']['vix']), 'tnx': prices.load(u['macro']['tnx']),
             'usdnok': prices.load(u['macro']['usdnok']), 'brent': prices.load(u['macro']['brent']),
             'spx': bench.get('US')}
    macro = {k: v for k, v in macro.items() if v is not None}
    funds = {x['t']: sec.load(x['t']) for x in u['stocks'] if x['region'] == 'US'}
    return u, px, bench, macro, funds

def build_panel(u, px, bench, macro, funds=None, with_targets=True):
    funds = funds or {}
    frames = []
    for x in u['stocks']:
        t, region = x['t'], x['region']
        if t not in px: continue
        s = px[t].dropna(); s = s[~s.index.duplicated(keep='last')].sort_index()
        b = bench.get(region)
        b = b[~b.index.duplicated(keep='last')] if b is not None else pd.Series(np.nan, index=s.index)
        f = pd.concat([price_features(s, b), macro_frame(s.index, macro), fundamental_features(s, funds.get(t))], axis=1)
        f['is_no'] = 1.0 if region == 'NO' else 0.0
        f['ticker'] = t; f['region'] = region; f['px'] = s
        if with_targets:
            bs = b.reindex(s.index.union(b.index)).ffill().reindex(s.index)
            for k, h in HORIZONS.items():
                n = h['trading']
                f[f'ret_{k}'] = s.shift(-n) / s - 1
                f[f'exc_{k}'] = f[f'ret_{k}'] - (bs.shift(-n) / bs - 1)
        frames.append(f)
    panel = pd.concat(frames)
    panel.index.name = 'date'
    return panel.reset_index()

def sample_rows(panel):
    """Weekly rows only, so overlapping 1m/3m windows do not masquerade as independent evidence."""
    return pd.concat([g.iloc[::SAMPLE_EVERY] for _, g in panel.groupby('ticker')])
