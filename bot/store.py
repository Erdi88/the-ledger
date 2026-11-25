"""Append-only prediction log. Rows are never edited; outcomes are written separately once the horizon passes."""
import json
from .config import DATA

PRED, OUT = DATA / 'predictions.jsonl', DATA / 'outcomes.jsonl'

def read(path):
    if not path.exists(): return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]

def append(path, rows):
    if not rows: return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a') as f:
        for r in rows: f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + '\n')
    return len(rows)

def pred_id(date, ticker, horizon): return f'{date}-{ticker}-{horizon}'
