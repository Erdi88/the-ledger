"""Validate external diagnostic evidence; optionally apply reviewed enablement."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from collector.probe import ingest

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('results', type=Path)
    parser.add_argument('--apply', action='store_true', help='Apply only independently reviewed, healthy source enablement')
    args = parser.parse_args()
    try:
        print(json.dumps(ingest(args.results, apply=args.apply), indent=2))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        raise SystemExit('Import refused: '+str(exc))
