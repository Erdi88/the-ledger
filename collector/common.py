"""Small shared serialization and timestamp helpers; no third-party runtime dependencies."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
UTC=dt.timezone.utc
OSLO=ZoneInfo('Europe/Oslo')
def config(name): return json.loads((ROOT/'config'/f'{name}.json').read_text())
def instant(value):
 if not isinstance(value,str): raise ValueError('timestamp missing')
 result=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
 if result.tzinfo is None: raise ValueError('timezone required')
 return result.astimezone(UTC)
def stamp(value): return value.astimezone(UTC).isoformat().replace('+00:00','Z')
def digest(value): return hashlib.sha256(value.encode()).hexdigest()
def atomic(path,value):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_suffix(path.suffix+'.tmp')
 temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
 os.replace(temp,path)
def load(path,default=None):
 try:return json.loads(Path(path).read_text())
 except FileNotFoundError:return default
