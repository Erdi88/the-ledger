"""CLI: python -m bot.run [update|eval|predict|resolve|report|daily]"""
import argparse, datetime as dt, json, sys
import numpy as np
import pandas as pd
from . import features, model, principles, prices, report, resolve, sec, store
from .config import DATA, HORIZONS, MODEL_VERSION, UP_THRESHOLD, DOWN_THRESHOLD, universe

def tickers():
    u = universe()
    return [x['t'] for x in u['stocks']] + list(u['benchmarks'].values()) + list(u['macro'].values())

def cmd_update(args):
    u = universe()
    status = {'prices': prices.update(tickers())}
    fund_dir = DATA / 'fundamentals'
    stale = args.force or not fund_dir.exists() or not any(fund_dir.glob('*.csv')) or \
        (dt.datetime.now().timestamp() - min(p.stat().st_mtime for p in fund_dir.glob('*.csv'))) > 7 * 86400
    if stale:
        status['fundamentals'] = sec.update([x['t'] for x in u['stocks'] if x['region'] == 'US'])
    bad = {k: v for k, v in status['prices'].items() if not v['ok']}
    print(f"prices ok {len(status['prices']) - len(bad)}/{len(status['prices'])}", 'failed: ' + ', '.join(bad) if bad else '')
    if 'fundamentals' in status:
        f = status['fundamentals']; print(f"fundamentals ok {sum(v['ok'] for v in f.values())}/{len(f)}")
    (DATA / 'update_status.json').write_text(json.dumps(status, indent=1))
    return status

def _panel(with_targets=True):
    u, px, bench, macro, funds = features.load_all()
    return u, px, bench, features.build_panel(u, px, bench, macro, funds, with_targets)

def cmd_eval(args):
    _, _, _, panel = _panel()
    res = {'evaluated_at': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'model': MODEL_VERSION,
           'method': 'Walk-forward: for each test year the model trains only on data ending a full horizon before that year starts.',
           'universe_size': int(panel['ticker'].nunique()), 'horizons': model.walk_forward(panel)}
    hs = res['horizons'].values()
    res['edge_demonstrated'] = bool(hs) and all((m['auc'] or 0) >= 0.53 and m['brier'] < m['brier_baseline'] for m in hs)
    res['edge_rule'] = 'Edge counts as demonstrated only if out-of-sample AUC >= 0.53 AND Brier score beats always-guessing-the-base-rate, at every horizon.'
    (DATA / 'model_eval.json').write_text(json.dumps(res, indent=1, allow_nan=False))
    for h, m in res['horizons'].items():
        print(f"{h}: n={m['n']} hit={m['hit_rate']:.3f} baseline={m['base_hit_rate']:.3f} auc={m['auc'] and round(m['auc'], 3)} "
              f"brier={m['brier']:.4f} vs {m['brier_baseline']:.4f}")
    return res

def cmd_predict(args):
    u, px, bench, panel = _panel()
    today = panel['date'].max()
    existing = store.read(store.PRED)
    made = {(p['ticker'], p['horizon']): p['made_at'] for p in existing}
    new, latest = [], panel.sort_values('date').groupby('ticker').tail(1).set_index('ticker')
    for k, h in HORIZONS.items():
        col = f'ret_{k}'
        train = panel.dropna(subset=[col, 'px'])
        train = train[train['date'] <= today - pd.Timedelta(days=h['calendar'])]
        train = features.sample_rows(train)
        rows = latest[(today - latest['date']).dt.days <= 7]
        if rows.empty or len(train) < 1000: continue
        p, logit = model.fit_predict(train, rows.reset_index(), col)
        for (t, row), pu in zip(rows.iterrows(), p):
            made_on = row['date'].date().isoformat()
            prev = made.get((t, k))
            if prev and (dt.date.fromisoformat(made_on) - dt.date.fromisoformat(prev)).days < 7: continue   # weekly cadence
            flags = principles.red_flags(row); mos, why = principles.margin_of_safety(row)
            call = 'UP' if pu >= UP_THRESHOLD else 'DOWN' if pu <= DOWN_THRESHOLD else 'ABSTAIN'
            blocked = None
            if call == 'UP' and flags: call, blocked = 'ABSTAIN', 'red flags (inversion rule)'
            due = (row['date'] + pd.Timedelta(days=h['calendar'])).date().isoformat()
            new.append({'id': store.pred_id(made_on, t, k), 'made_at': made_on, 'ticker': t, 'region': row['region'], 'horizon': k,
                        'due_date': due, 'price': round(float(row['px']), 4), 'p_up': round(float(pu), 4), 'call': call,
                        'blocked_by': blocked, 'red_flags': flags, 'margin_of_safety': mos, 'mos_reasons': why,
                        'capital_allocation': principles.capital_allocation(row),
                        'drivers': model.drivers(logit, row) if logit is not None else [],
                        'model': MODEL_VERSION, 'n_train': int(len(train))})
    n = store.append(store.PRED, new)
    print(f'{n} new predictions', {c: sum(x['call'] == c for x in new) for c in ('UP', 'DOWN', 'ABSTAIN')})
    return new

def cmd_resolve(args):
    u, px, bench, macro, funds = features.load_all()
    new = resolve.resolve(px, bench)
    print(f'{store.append(store.OUT, new)} predictions resolved')
    return new

def cmd_report(args):
    sc = report.scorecard(); report.write(sc)
    print(json.dumps(sc['totals'])); return sc

def cmd_daily(args):
    cmd_update(args)
    ev = DATA / 'model_eval.json'
    age = 10 ** 9
    if ev.exists():   # file mtime is meaningless after a git checkout, so read the timestamp inside the file
        at = dt.datetime.fromisoformat(json.loads(ev.read_text())['evaluated_at'].replace('Z', '+00:00'))
        age = (dt.datetime.now(dt.timezone.utc) - at).days
    if args.eval or age > 30:
        cmd_eval(args)
    cmd_resolve(args); cmd_predict(args); cmd_report(args)

def main(argv=None):
    p = argparse.ArgumentParser(prog='bot')
    p.add_argument('command', choices=['update', 'eval', 'predict', 'resolve', 'report', 'daily'])
    p.add_argument('--force', action='store_true'); p.add_argument('--eval', action='store_true')
    a = p.parse_args(argv)
    globals()['cmd_' + a.command](a)
if __name__ == '__main__': main()
