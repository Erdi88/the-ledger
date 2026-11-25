"""Walk-forward evaluation and fitting. Honest by construction: purge gap, no future rows, baseline always shown."""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from .config import HORIZONS, UP_THRESHOLD, DOWN_THRESHOLD
from .features import FEATURES

def make_models():
    logit = make_pipeline(SimpleImputer(strategy='median', keep_empty_features=True), StandardScaler(),
                          LogisticRegression(C=0.05, max_iter=500))
    hgb = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=150, l2_regularization=2.0,
                                         min_samples_leaf=150, random_state=0)
    return logit, hgb

def fit_predict(train, test_X, y_col):
    y = (train[y_col] > 0).astype(int)
    if y.nunique() < 2 or len(train) < 200:
        return np.full(len(test_X), float(y.mean()) if len(y) else 0.5), None
    logit, hgb = make_models()
    X = train[FEATURES].replace([np.inf, -np.inf], np.nan)
    cols = [c for c in FEATURES if X[c].nunique() > 1]       # constant/empty columns break binning and carry no signal
    T = test_X[cols].replace([np.inf, -np.inf], np.nan)
    logit.fit(X[cols], y); hgb.fit(X[cols], y)
    logit.feature_cols = cols
    p = 0.5 * logit.predict_proba(T)[:, 1] + 0.5 * hgb.predict_proba(T)[:, 1]
    return p, logit

def _metrics(y, p, base):
    y = np.asarray(y); p = np.clip(np.asarray(p), 1e-4, 1 - 1e-4)
    out = {'n': int(len(y)), 'hit_rate': float(((p > 0.5) == (y == 1)).mean()),
           'base_hit_rate': float(max(y.mean(), 1 - y.mean())), 'up_share': float(y.mean()),
           'brier': float(brier_score_loss(y, p)), 'brier_baseline': float(brier_score_loss(y, np.full(len(y), base))),
           'logloss': float(log_loss(y, p, labels=[0, 1]))}
    out['auc'] = float(roc_auc_score(y, p)) if len(set(y)) > 1 else None
    conf = (p >= UP_THRESHOLD) | (p <= DOWN_THRESHOLD)
    out['confident_n'] = int(conf.sum())
    out['confident_hit_rate'] = float(((p[conf] > 0.5) == (y[conf] == 1)).mean()) if conf.any() else None
    return out

def walk_forward(panel, first_test_year=2012):
    """Train on everything strictly before (test-year start minus horizon), test on the year. Repeat."""
    panel = panel.dropna(subset=['px']).copy()
    panel['year'] = panel['date'].dt.year
    result = {}
    for k, h in HORIZONS.items():
        col, exc = f'ret_{k}', f'exc_{k}'
        d = panel.dropna(subset=[col])
        preds = []
        for yr in range(first_test_year, int(d['year'].max()) + 1):
            test = d[d['year'] == yr]
            cutoff = pd.Timestamp(f'{yr}-01-01') - pd.Timedelta(days=int(h['calendar']))
            train = d[d['date'] < cutoff]
            if test.empty or len(train) < 1000: continue
            p, _ = fit_predict(train, test, col)
            preds.append(pd.DataFrame({'date': test['date'].values, 'ticker': test['ticker'].values, 'year': yr, 'p': p,
                                       'y': (test[col] > 0).astype(int).values, 'ret': test[col].values,
                                       'exc': test[exc].values, 'base': float((train[col] > 0).mean())}))
        if not preds: continue
        r = pd.concat(preds)
        m = _metrics(r['y'], r['p'], r['base'].mean())
        up, dn = r[r['p'] >= UP_THRESHOLD], r[r['p'] <= DOWN_THRESHOLD]
        m['mean_ret_when_up'] = float(up['ret'].mean()) if len(up) else None
        m['mean_ret_when_down'] = float(dn['ret'].mean()) if len(dn) else None
        m['mean_ret_all'] = float(r['ret'].mean())
        q = r['p'].rank(pct=True)
        m['mean_ret_top_quintile'] = float(r.loc[q > 0.8, 'ret'].mean())
        m['mean_ret_bottom_quintile'] = float(r.loc[q <= 0.2, 'ret'].mean())
        m['by_year'] = {int(y): {'n': int(len(g)), 'hit_rate': float(((g['p'] > 0.5) == (g['y'] == 1)).mean()),
                                 'base_hit_rate': float(max(g['y'].mean(), 1 - g['y'].mean()))} for y, g in r.groupby('year')}
        bins = pd.cut(r['p'], [0, 0.4, 0.45, 0.5, 0.55, 0.6, 1.0])
        m['calibration'] = [{'bin': str(b), 'n': int(len(g)), 'predicted': float(g['p'].mean()), 'actual_up': float(g['y'].mean())}
                            for b, g in r.groupby(bins, observed=True)]
        result[k] = m
    return result

def drivers(logit, row, top=3):
    """Plain-language reasons: the largest standardized logistic contributions for this stock today."""
    try:
        imp, sc, lr = logit.steps[0][1], logit.steps[1][1], logit.steps[2][1]
        cols = logit.feature_cols
        z = sc.transform(imp.transform(row[cols].to_frame().T.astype(float).replace([np.inf, -np.inf], np.nan)))[0]
        contrib = z * lr.coef_[0]
        idx = np.argsort(-np.abs(contrib))[:top]
        return [{'feature': cols[i], 'value': None if pd.isna(row[cols[i]]) or np.isinf(row[cols[i]]) else round(float(row[cols[i]]), 4),
                 'pushes': 'up' if contrib[i] > 0 else 'down'} for i in idx]
    except Exception:
        return []
