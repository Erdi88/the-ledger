"""Golden checks use returned LIVE probe headlines as probe samples, not fixtures."""
import json
import unittest
from pathlib import Path
from collector.topic import topic_decision
from collector.rank import select_top

ROOT=Path(__file__).resolve().parents[1]
PROBE=json.loads((ROOT/'live_probe_results.json').read_text())
SAMPLES={s['source_id']:[i for i in s.get('items',[]) if i.get('headline')] for s in PROBE['results']}

def sample(source,needle):
 return next(i for i in SAMPLES[source] if needle.casefold() in i['headline'].casefold())

class ProbeSampleGoldens(unittest.TestCase):
 def test_required_keep_probe_samples(self):
  examples=[('cnbc','China Connection'),('cnbc','Starbucks says it is not buying Chipotle'),('cnbc','older Americans'),('e24','Inntektshopp for ABG'),('e24','Nel varsler Rheinmetall'),('e24','Kraftig tekfall'),('e24','Nobelprisen i økonomi'),('e24','Shippingvinner'),('e24','Milliardveddemål mot bilaksje'),('e24','Resultatrush'),('e24','høyere prisvekst'),('e24','diesel-slipp'),('e24','boligprisene')]
  for source,needle in examples:
   item=sample(source,needle);d=topic_decision(item['headline'],item['link'],{'id':source})
   self.assertEqual(d['outcome'],'KEEP',f"{item['headline']}: {d}")

 def test_flexible_probe_samples_never_drop(self):
  examples=[('cnbc','Russia diesel deal'),('cnbc','homegrown AI chips'),('cnbc',"McDonald's is leaning"),('e24','Mark Zuckerberg'),('e24','Sara Midtgaard'),('e24','Telia nedbemanner'),('e24','Google må stanse datasenter'),('cnbc','Saudi Arabia says drones'),('e24','Fastlåst i Midtøsten'),('e24','stans i energi-angrep')]
  for source,needle in examples:
   item=sample(source,needle);d=topic_decision(item['headline'],item['link'],{'id':source})
   self.assertIn(d['outcome'],('KEEP','LOW_CONFIDENCE'),f"{item['headline']}: {d}")

 def test_required_drop_probe_samples(self):
  examples=[('cnbc','Ilhan Omar'),('cnbc','Kimberly Guilfoyle'),('cnbc','midterm donor'),('e24','mellomvalget'),('cnbc',"Red Bull's F1 team"),('cnbc','calculator to explain'),('e24','Konsulent-toppene'),('e24','jobbsøknad for maskiner'),('e24','jobbsøknaden din'),('e24','lungebetennelse'),('e24','Epstein-varsler'),('e24','Gard Steiro'),('e24','trainee-stillinger'),('cnbc','FAA warns U.S. airlines'),('cnbc','Delta delays debut')]
  for source,needle in examples:
   item=sample(source,needle);d=topic_decision(item['headline'],item['link'],{'id':source})
   self.assertEqual(d['outcome'],'DROP',f"{item['headline']}: {d}")

 def test_e24_sections_and_compounds(self):
  self.assertEqual(topic_decision('Something','https://e24.no/karriere-og-ledelse/x/y',{'id':'e24'})['outcome'],'DROP')
  self.assertEqual(topic_decision('Something','https://e24.no/boers-og-finans/x/y',{'id':'e24'})['outcome'],'LOW_CONFIDENCE')
  for section in ('norsk-oekonomi','internasjonal-oekonomi'):
   self.assertEqual(topic_decision('Something','https://e24.no/'+section+'/x/y',{'id':'e24'})['outcome'],'LOW_CONFIDENCE')
  for section in ('naeringsliv','energi-og-klima'):
   url='https://e24.no/'+section+'/x/y'
   self.assertEqual(topic_decision('Something',url,{'id':'e24'})['outcome'],'LOW_CONFIDENCE')
   self.assertEqual(topic_decision('Diesel supply',url,{'id':'e24'})['outcome'],'KEEP')
  self.assertEqual(topic_decision('bilaksje', 'https://example.org',{})['outcome'],'KEEP')
  self.assertEqual(topic_decision('Trump diesel deal','https://example.org',{})['outcome'],'KEEP')

 def test_low_confidence_never_enters_top_five(self):
  rows=[{'event_type':'research','topic_outcome':'LOW_CONFIDENCE','editorial_score':5,'published_at':'2026-10-13T00:00:00Z','id':'low','publisher':'A','asset_classes':['macro']}]
  rows += [{'event_type':'research','topic_outcome':'KEEP','editorial_score':4,'published_at':'2026-10-13T00:00:00Z','id':str(n),'publisher':'P'+str(n),'asset_classes':['macro']} for n in range(5)]
  top=select_top(rows)
  self.assertEqual(len(top),5)
  self.assertTrue(all(i['topic_outcome']=='KEEP' for i in top))

 def test_required_word_boundaries_and_unique_matches(self):
  cases=[('Oil markets remain in turmoil','oil'),('Chipotle expands stores','chip'),('SoftBank changes leadership','bank'),("Fed's decision",'fed')]
  self.assertEqual(topic_decision(cases[0][0])['outcome'],'KEEP')
  self.assertNotIn('chip',topic_decision(cases[1][0])['rule'].casefold())
  self.assertNotIn('bank',topic_decision(cases[2][0])['rule'].casefold())
  self.assertIn('fed',topic_decision(cases[3][0])['rule'].casefold())
  for title in ('Hammack','Hammack speaks'):
   terms=[term.casefold() for term in topic_decision(title)['matched_terms']]
   self.assertNotIn('eia',terms);self.assertNotIn('sec',terms)
  self.assertEqual(topic_decision('Oil oil prices')['rule'].count('oil'),1)

 def test_generic_terms_alone_are_not_confident_keeps(self):
  for word in ('market','retail','trade','price','regnskap','inntekt'):
   self.assertEqual(topic_decision(word)['outcome'],'DROP',word)
  self.assertEqual(topic_decision('oil trade')['outcome'],'KEEP')

 def test_technology_product_needs_financial_signal(self):
  for title in ('Meta debuts AI model','Microsoft homegrown AI chips'):
   self.assertEqual(topic_decision(title)['outcome'],'LOW_CONFIDENCE',title)
  for title in ('Meta AI model revenue rises','Microsoft AI chips deal'):
   self.assertEqual(topic_decision(title)['outcome'],'KEEP',title)

 def test_ft_probe_sample_batch_is_classifiable(self):
  self.assertEqual(len(SAMPLES['ft']),10)
  for item in SAMPLES['ft']:
   d=topic_decision(item['headline'],item['link'],{'id':'ft'})
   self.assertIn(d['outcome'],('KEEP','LOW_CONFIDENCE','DROP'))

if __name__=='__main__':unittest.main()
