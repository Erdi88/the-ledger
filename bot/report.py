"""Scorecard: did the bot's calls beat guessing 'up' every time? Written to JSON for the site."""
import datetime as dt, json
import numpy as np
from . import store
from .config import DATA, SITE_DATA, HORIZONS

def _rate(xs): return None if not xs else float(np.mean(xs))

def scorecard(now=None):
    preds, outs = store.read(store.PRED), {o['id']: o for o in store.read(store.OUT)}
    sc = {'generated_at': (now or dt.datetime.now(dt.timezone.utc)).strftime('%Y-%m-%dT%H:%M:%SZ'),
          'disclaimer': 'Research experiment, not investment advice. Predictions are statistical guesses with no guarantee. Past results do not predict future ones.',
          'totals': {'predictions': len(preds), 'resolved': sum(p['id'] in outs for p in preds),
                     'pending': sum(p['id'] not in outs for p in preds)}, 'by_horizon': {}}
    for h in HORIZONS:
        rows = [(p, outs[p['id']]) for p in preds if p['horizon'] == h and p['id'] in outs]
        called = [(p, o) for p, o in rows if p['call'] != 'ABSTAIN']
        ups = [o['realized_return'] for p, o in rows if p['call'] == 'UP']
        dns = [o['realized_return'] for p, o in rows if p['call'] == 'DOWN']
        allr = [o['realized_return'] for p, o in rows]
        mos = [(o['correct']) for p, o in called if p.get('margin_of_safety') is True]
        nomos = [(o['correct']) for p, o in called if p.get('margin_of_safety') is False]
        flagged = [o['correct'] for p, o in called if p.get('red_flags')]
        brier = [(p['p_up'] - (1.0 if o['went_up'] else 0.0)) ** 2 for p, o in rows]
        base_p = _rate([1.0 if o['went_up'] else 0.0 for _, o in rows])
        sc['by_horizon'][h] = {
            'resolved': len(rows), 'called': len(called), 'abstained': len(rows) - len(called),
            'hit_rate': _rate([o['correct'] for _, o in called]),
            'always_up_hit_rate': _rate([1.0 if o['went_up'] else 0.0 for _, o in called]),
            'mean_return_when_up': _rate(ups), 'mean_return_when_down': _rate(dns), 'mean_return_all': _rate(allr),
            'brier': _rate(brier),
            'brier_if_always_base_rate': None if base_p is None else _rate([(base_p - (1.0 if o['went_up'] else 0.0)) ** 2 for _, o in rows]),
            'hit_rate_margin_of_safety_pass': _rate(mos), 'hit_rate_margin_of_safety_fail': _rate(nomos),
            'hit_rate_with_red_flags': _rate(flagged)}
    recent = sorted(preds, key=lambda p: (p['made_at'], p['ticker']), reverse=True)[:60]
    sc['recent'] = [{'made_at': p['made_at'], 'ticker': p['ticker'], 'horizon': p['horizon'], 'due_date': p['due_date'],
                     'call': p['call'], 'p_up': round(p['p_up'], 3), 'price': p['price'], 'red_flags': p.get('red_flags', []),
                     'margin_of_safety': p.get('margin_of_safety'), 'drivers': p.get('drivers', []),
                     'result': ({'return': outs[p['id']]['realized_return'], 'correct': outs[p['id']]['correct']} if p['id'] in outs else None)}
                    for p in recent]
    ev = DATA / 'model_eval.json'
    sc['backtest'] = json.loads(ev.read_text()) if ev.exists() else None
    return sc

def write(sc):
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    (SITE_DATA / 'bot_scorecard.json').write_text(json.dumps(sc, indent=1, ensure_ascii=False, allow_nan=False))
