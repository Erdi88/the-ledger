"""Grade matured predictions against what the price actually did."""
import datetime as dt
import pandas as pd
from . import store

def price_on_or_after(s, day):
    s = s[s.index >= pd.Timestamp(day)]
    return (s.index[0].date().isoformat(), float(s.iloc[0])) if len(s) else None

def resolve(px, bench, today=None):
    preds, outs = store.read(store.PRED), {o['id'] for o in store.read(store.OUT)}
    new = []
    for p in preds:
        if p['id'] in outs: continue
        s = px.get(p['ticker'])
        if s is None: continue
        hit = price_on_or_after(s, p['due_date'])
        if not hit: continue
        day, price = hit
        # the price must really be at/after the due date, not a stale last quote
        if pd.Timestamp(day) - pd.Timestamp(p['due_date']) > pd.Timedelta(days=7): continue
        ret = price / p['price'] - 1
        b = bench.get(p['region']); bret = None
        if b is not None:
            b0, b1 = price_on_or_after(b, p['made_at']), price_on_or_after(b, p['due_date'])
            if b0 and b1: bret = b1[1] / b0[1] - 1
        went_up = ret > 0
        new.append({'id': p['id'], 'resolved_on': day, 'price_due': round(price, 4), 'realized_return': round(ret, 5),
                    'benchmark_return': None if bret is None else round(bret, 5),
                    'excess_return': None if bret is None else round(ret - bret, 5),
                    'went_up': went_up,
                    'correct': None if p['call'] == 'ABSTAIN' else (went_up == (p['call'] == 'UP'))})
    return new
