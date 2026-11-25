"""Direct DNS/HTTPS evidence, never a license approval or a collection substitute."""
import concurrent.futures, datetime, json, pathlib, socket, time, urllib.parse, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from collector.http import Client
def probe(source):
 start=time.monotonic(); host=urllib.parse.urlsplit(source['url']).hostname
 row={'id':source['id'],'url':source['url'],'attempted_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'http_status':None,'format':'unknown','status':'TESTED-OFFLINE','usable':False}
 try:
  socket.getaddrinfo(host,443)
  # The actual collector performs robots, terms, IP, and format checks. A HEAD probe
  # is only availability evidence and deliberately retrieves no article body.
  client=Client(source,ROOT/'data/cache')
  client.allowed(source['url'])
  status,headers,_,_=client.raw(source['url'],method='HEAD')
  row.update(http_status=status,format=headers.get('content-type','unknown'),status='LIVE-VERIFIED',note='HEAD availability only; parser and reuse rights NOT verified')
 except Exception as exc: row['error']=str(exc)
 row['latency_ms']=round((time.monotonic()-start)*1000,1)
 return row
if __name__=='__main__':
 sources=json.loads((ROOT/'config/sources.json').read_text())
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(probe,sources))
 (ROOT/'evidence/source-probes.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(json.dumps({'attempts':len(rows),'http_responses':sum(x['http_status'] is not None for x in rows),'usable_sources':0,'evidence':'evidence/source-probes.json'}))
