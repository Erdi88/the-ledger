import json, os, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = pathlib.Path(os.environ.get('LEDGER_BOT_DATA', ROOT / 'bot_data'))
SITE_DATA = ROOT / 'site' / 'data'
# Horizons: trading days used for training labels, calendar days used for resolving a live prediction.
HORIZONS = {'1m': {'trading': 21, 'calendar': 30}, '3m': {'trading': 63, 'calendar': 91}}
UP_THRESHOLD, DOWN_THRESHOLD = 0.57, 0.43   # between these the bot abstains instead of guessing
SAMPLE_EVERY = 5                            # weekly rows keep overlapping labels from swamping the model
MODEL_VERSION = 'v1-ensemble-logit-hgb'
def universe():
    return json.loads((ROOT / 'bot' / 'universe.json').read_text())
def contact():
    return os.environ.get('LEDGER_CONTACT_EMAIL', '').strip() or 'personal-research'
