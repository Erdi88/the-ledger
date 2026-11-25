"""Bounded HTTPS, pinned public DNS, robots, conditional metadata cache."""
import http.client
import ipaddress
import json
import os
import socket
import ssl
import time
import urllib.parse
import urllib.robotparser
import re
import zlib
from .common import atomic,digest,load
MAX_BYTES=2_000_000
class FetchError(ValueError):
 def __init__(self,message,redirect_domain=None,robots_status=None):
  super().__init__(message);self.redirect_domain=redirect_domain;self.robots_status=robots_status

def check_url(url,domains):
 p=urllib.parse.urlsplit(url)
 if p.scheme!='https' or not p.hostname or p.hostname not in domains or p.username or p.password or p.port not in (None,443):
  raise FetchError('HTTPS allowlist violation')
 if any(ord(c)<32 for c in url):raise FetchError('control character in URL')
 return p

def public_addresses(host):
 records=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
 addresses=list(dict.fromkeys(r[4][0] for r in records))
 if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses):raise FetchError('non-public address blocked')
 return addresses

class PinnedHTTPS(http.client.HTTPSConnection):
 def __init__(self,host,address):
  super().__init__(host,timeout=12,context=ssl.create_default_context()); self.address=address
 def connect(self):
  sock=socket.create_connection((self.address,443),self.timeout)
  self.sock=self._context.wrap_socket(sock,server_hostname=self.host)

class Client:
 def __init__(self,source,cache_dir):
  self.source=source;self.cache_dir=cache_dir;self.last_request=0
  contact=os.environ.get('LEDGER_CONTACT_EMAIL','').strip()
  if source['id'].startswith('fixture-') and not contact:contact='fixture@example.org'
  if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',contact):
   raise FetchError('Set LEDGER_CONTACT_EMAIL to a real contact email for all source requests')
  self.ua=f'TheLedger/0.1 (metadata-only financial reader; contact: {contact})'
  self.robots={};self.robots_status=None
 def raw(self,url,headers=None,redirects=0,method='GET'):
  if redirects>3:raise FetchError('redirect limit')
  p=check_url(url,self.source['allowed_domains']);addresses=public_addresses(p.hostname)
  time.sleep(max(0,self.source.get('min_interval_seconds',2)-(time.monotonic()-self.last_request)))
  self.last_request=time.monotonic()
  conn=PinnedHTTPS(p.hostname,addresses[0])
  try:
   conn.request(method,urllib.parse.urlunsplit(('', '', p.path or '/',p.query,'')),headers={'User-Agent':self.ua,'Accept-Encoding':'gzip, identity',**(headers or {})})
   response=conn.getresponse(); status=response.status; hs={k.lower():v for k,v in response.getheaders()}
   if status in (301,302,303,307,308):
    target=urllib.parse.urljoin(url,hs.get('location',''))
    domain=urllib.parse.urlsplit(target).hostname
    try:check_url(target,self.source['allowed_domains'])
    except FetchError as exc:raise FetchError(str(exc),redirect_domain=domain) from exc
    # Robots rules apply to each redirect destination too.
    if not p.path.endswith('/robots.txt'):self.allowed(target)
    return self.raw(target,headers,redirects+1,method)
   length=int(hs.get('content-length',0))
   if length>MAX_BYTES:raise FetchError('response too large')
   encoding=hs.get('content-encoding','identity').lower()
   if encoding not in ('identity','gzip'):raise FetchError('unsupported content encoding')
   decoder=zlib.decompressobj(16+zlib.MAX_WBITS) if encoding=='gzip' else None
   chunks=[];size=0;compressed_size=0;deadline=time.monotonic()+30
   while True:
    remaining=deadline-time.monotonic()
    if remaining<=0:raise FetchError('response deadline exceeded')
    if conn.sock:conn.sock.settimeout(min(12,remaining))
    chunk=response.read1(65536)
    if not chunk:break
    compressed_size+=len(chunk)
    if compressed_size>MAX_BYTES:raise FetchError('compressed response too large')
    try:
     decoded=decoder.decompress(chunk,MAX_BYTES+1-size) if decoder else chunk
    except zlib.error as exc:raise FetchError('invalid gzip response') from exc
    chunks.append(decoded);size+=len(decoded)
    if size>MAX_BYTES:raise FetchError('response too large')
    if decoder and decoder.unconsumed_tail:raise FetchError('decompressed response too large')
   if decoder:
    if not decoder.eof:raise FetchError('truncated gzip response')
    tail=decoder.flush(MAX_BYTES+1-size);chunks.append(tail);size+=len(tail)
    if size>MAX_BYTES:raise FetchError('decompressed response too large')
   body=b''.join(chunks)
   return status,hs,body,url
  finally:conn.close()
 def allowed(self,url):
  p=check_url(url,self.source['allowed_domains']);origin='https://'+p.hostname
  if origin not in self.robots:
   status,_,body,_=self.raw(origin+'/robots.txt')
   self.robots_status=status
   if status==404:rules=[]
   elif status==200:rules=body.decode('utf-8','replace').splitlines()
   else:raise FetchError(f'robots unavailable HTTP {status}',robots_status=status)
   parser=urllib.robotparser.RobotFileParser();parser.parse(rules);self.robots[origin]=parser
  parser=self.robots[origin]
  if not parser.can_fetch(self.ua,url):raise FetchError('robots disallows URL')
  delay=parser.crawl_delay(self.ua)
  if delay:self.source['min_interval_seconds']=max(delay,self.source.get('min_interval_seconds',2))
 def fetch(self):
  if not self.source.get('terms_approved'):raise FetchError('reuse terms not approved')
  self.allowed(self.source['url'])
  cache_path=self.cache_dir/(self.source['id']+'.json'); cache=load(cache_path,{})
  # A changed URL or policy cannot reuse the previous sanitized cache.
  policy=digest(str(sorted(self.source.items())))
  if cache.get('policy')!=policy:cache={}
  headers={}
  if cache.get('etag'):headers['If-None-Match']=cache['etag']
  if cache.get('last_modified'):headers['If-Modified-Since']=cache['last_modified']
  start=time.monotonic();status,hs,body,final=self.raw(self.source['url'],headers)
  meta={'http_status':status,'latency_ms':round((time.monotonic()-start)*1000,1),'final_url':final,'body_sha256':digest(body.hex())}
  if status==304:
   if 'items' not in cache:raise FetchError('304 without sanitized cache')
   return None,cache['items'],meta
  if status!=200:raise FetchError(f'HTTP {status}')
  self.pending={'policy':policy,'etag':hs.get('etag'),'last_modified':hs.get('last-modified')}
  return body,None,meta
 def save(self,items):
  payload={**self.pending,'items':items}
  if len(json.dumps(payload).encode())>MAX_BYTES:raise FetchError('sanitized cache too large')
  atomic(self.cache_dir/(self.source['id']+'.json'),payload)
