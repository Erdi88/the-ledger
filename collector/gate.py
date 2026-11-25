import argparse
import datetime as dt
from pathlib import Path
from .common import OSLO,UTC,load
from .schema import validate

def should_run(now,root):
 local=now.astimezone(OSLO)
 if (local.hour,local.minute)<(6,30):return False,'Before 06:30 Europe/Oslo'
 archive=Path(root)/'editions'/f'{local.date()}.json'
 edition=load(archive)
 if edition:
  try:
   validate(edition)
   if edition['deployable'] and not edition['fixture']:return False,'Valid edition already exists for Oslo date'
  except (ValueError,KeyError,TypeError):pass
 return True,'No valid edition for Oslo date; collect'
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--root',default='.');args=parser.parse_args()
 run,reason=should_run(dt.datetime.now(UTC),args.root)
 print(f'run={str(run).lower()}');print(reason)
 import os
 if os.environ.get('GITHUB_OUTPUT'):
  with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write(f'run={str(run).lower()}\n')
