"""RSS/Atom and explicit JSON/SEC schemas. Never persist a response body."""
import datetime as dt
import email.utils
import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin
from ..common import stamp,UTC
class Plain(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,data):self.parts.append(data)
def plain(value):
 p=Plain();p.feed(value or '');return ' '.join(' '.join(p.parts).split())
def date(value):
 if not value:raise ValueError('missing publication time')
 if re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b',value,re.I) and not re.search(r'\b\d{4}\b',value):
  raise ValueError('yearless publication date rejected: '+value[:80])
 try:
  d=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
 except ValueError:d=email.utils.parsedate_to_datetime(value)
 if d.tzinfo is None:
  if re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):d=d.replace(tzinfo=UTC)
  else:raise ValueError('ambiguous timezone')
 return stamp(d)
def parse(body,source):
 adapter=source['adapter']
 if adapter in ('rss','atom'):
  if b'<!DOCTYPE' in body.upper() or b'<!ENTITY' in body.upper():raise ValueError('XML declarations blocked')
  root=ET.fromstring(body)
  if root.tag.split('}')[-1] not in ('rss','feed','RDF'):raise ValueError('unexpected feed root')
  if root.tag.split('}')[-1] in ('rss','RDF') and not any(child.tag.split('}')[-1]=='channel' for child in root):
   raise ValueError('feed channel structure missing')
  rows=[]
  for node in root.iter():
   if node.tag.split('}')[-1] not in ('item','entry'):continue
   fields={child.tag.split('}')[-1]:child for child in node}
   def val(key):return ''.join(fields[key].itertext()).strip() if key in fields else ''
   links=[c for c in node if c.tag.split('}')[-1]=='link' and c.get('rel','alternate')=='alternate']
   url=(links[0].get('href') or links[0].text or '') if links else ''
   title=val('title'); published=val('published') or val('pubDate') or val('date')
   # Atom updated is a revision time, never silently substituted for published.
   if not title or not url or not published:raise ValueError('feed canary missing title/link/published')
   rows.append({'title':title,'url':urljoin(source['url'],url),'published_at':date(published),'publication_precision':'instant','document_id':val('id') or val('guid') or url,'summary':plain(val('description') or val('summary'))})
  return rows
 if adapter=='sec':
  data=json.loads(body);recent=data['filings']['recent'];cik=str(int(data['cik']))
  required=['accessionNumber','form','filingDate','primaryDocument']
  count=len(recent['accessionNumber'])
  if any(len(recent[k])!=count for k in required):raise ValueError('SEC column lengths changed')
  return [{'title':f"{data['name']} — {recent['form'][i]} filing",'url':f"https://www.sec.gov/Archives/edgar/data/{cik}/{recent['accessionNumber'][i].replace('-','')}/{recent['primaryDocument'][i]}",'published_at':date(recent['filingDate'][i]),'publication_precision':'day','document_id':recent['accessionNumber'][i],'summary':'','event_type':'filing','instrument_context':{'filing_form':recent['form'][i]}} for i in range(count)]
 if adapter=='json':
  data=json.loads(body)
  if not isinstance(data.get('items'),list):raise ValueError('JSON items canary missing')
  rows=[]
  for x in data['items']:
   rows.append({'title':x['title'],'url':x['url'],'published_at':date(x['published_at']),'publication_precision':'instant','document_id':x['id'],'summary':plain(x.get('summary',''))})
  return rows
 raise ValueError('adapter NOT BUILT; HTML scraping intentionally excluded')

def feed_kind(body):
 """Distinguish article feeds from directories of RSS/Atom feed links."""
 try:root=ET.fromstring(body)
 except ET.ParseError:return 'unknown'
 tag=root.tag.split('}')[-1]
 if tag not in ('rss','feed','RDF'):return 'unknown'
 nodes=[n for n in root.iter() if n.tag.split('}')[-1] in ('item','entry')]
 if not nodes:return 'feed'
 if all(any(c.tag.split('}')[-1]=='link' and re.search(r'(?:/rss(?:/|$|\?)|\.rss(?:\?|$)|/feed(?:/|$|\?))',c.get('href') or c.text or '',re.I) for c in n) for n in nodes):
  return 'feed_index'
 if all(not any(c.tag.split('}')[-1] in ('published','pubDate','date') for c in n) for n in nodes):
  return 'unknown'
 return 'feed'
