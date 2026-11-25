"""Three-outcome, deterministic topic filter for editorial candidates."""
import re
from urllib.parse import urlparse

# Explicit Norwegian stems may match inside compounds. Keep this list limited to
# Norwegian inflections/compounds; English words use whole-word matching.
NORWEGIAN_STEMS = (
    'aksj', 'rente', 'olje', 'børs', 'boers', 'resultat', 'prisvekst', 'bolig',
    'skip', 'shipping', 'inntektshopp', 'tekfall', 'økonomi', 'oekonomi',
    'økonom', 'oekonom', 'oppkjøp', 'oppkjop', 'inflasjon', 'valuta',
    'nedbemann', 'datasenter', 'samarbeid', 'regnskapsfører', 'regnskapsfoerer',
)

# These English terms are deliberately whole words, including their common
# explicit plural forms. In particular, chip != Chipotle and bank != SoftBank.
STRONG_TERMS = (
    'gold', 'yuan', 'takeover', 'acquire', 'acquires', 'acquired', 'merger',
    'buyout', 'wealth', 'nvidia', 'chip', 'chips', 'tariff', 'sanction',
    'sanctions', 'diesel', 'fed', 'rate', 'rates', 'oil', 'energy', 'earnings',
    'inflation', 'bond', 'bonds', 'yield', 'yields', 'currency', 'bank', 'banks',
    'fund', 'funds', 'etf', 'etfs', 'crypto', 'bitcoin', 'gdp', 'profit',
    'revenue', 'spending', 'shares', 'stock', 'stocks', 'deal', 'deals',
    'investment', 'investments', 'petroleum', 'eia',
    'ecb', 'imf', 'sec', 'dividend', 'dividends', 'consumer spending',
)

# These are useful context only when another economic signal or an E24 section
# provides context. They cannot produce a confident KEEP alone.
WEAK_TERMS = (
    'market', 'markets', 'retail', 'trade', 'price', 'prices', 'regnskap',
    'inntekt', 'income', 'sales', 'investment', 'investments', 'deal', 'deals',
    'consumer', 'layoff', 'departure', 'mcdonald', 'restaurant', 'saudi',
    'attacks', 'angrep', 'midtøsten', 'middle east', 'nobelprisen i økonomi',
    'nobelprisen i oekonomi',
)
FINANCIAL_TECH_TERMS = (
    'shares', 'deal', 'deals', 'earnings', 'acquire', 'acquires', 'acquired',
    'stock', 'stocks', 'investment', 'investments', 'revenue',
)
OFF_TOPIC_TERMS = (
    'campaign', 'midterm', 'donor', 'donation', 'ambassador', 'raid', 'epstein',
    'lifestyle', 'f1', 'formula 1', 'football', 'soccer', 'sport', 'racing',
    'grand prix', 'jobbsøknad', 'jobbsoknad', 'trainee-stilling', 'trainee-stillinger', 'trainee stilling',
    'drømmejobb', 'drommejobb', 'career advice', 'lungebetennelse', 'pneumonia',
    'sjefredaktør', 'sjefredaktor', 'editor-in-chief', 'editor in chief',
    'calculator', 'airlines', 'airline safety', 'flight delay', 'aviation safety',
    'delays debut', 'airport attacks', 'senator', 'mellomvalget', 'valgkamp',
    'donasjoner', 'red bull f1',
)
WEAK_CONTEXT_TERMS = (
    'mcdonald', 'restaurant', 'consumer', 'layoff', 'nedbemann',
    'markets departure', 'departure', 'datasenter', 'data center', 'saudi',
    'attacks', 'angrep', 'midtøsten', 'middle east', 'møte-smell', 'ai',
)
E24_KEEP_DEFAULT = {'boers-og-finans', 'norsk-oekonomi', 'internasjonal-oekonomi'}
E24_LOW_DEFAULT = {'naeringsliv', 'energi-og-klima'}
E24_DENIED = {'karriere-og-ledelse'}


def _unique(values):
    result=[];seen=set()
    for value in values:
        key=value.casefold()
        if key not in seen:
            seen.add(key);result.append(value)
    return result


def _has(text, terms):
    """Match Norwegian stems as substrings, English terms at word boundaries."""
    folded=text.casefold();found=[]
    for term in terms:
        if term in NORWEGIAN_STEMS:
            matched=term.casefold() in folded
        else:
            matched=bool(re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',text,re.I))
        if matched:found.append(term)
    return _unique(found)


def _tech_product(title):
    return bool(re.search(r'\b(?:ai|artificial intelligence)\b.{0,45}\b(?:model|models|modell|modeller|chip|chips)\b|'
                          r'\b(?:model|models|modell|modeller|chip|chips)\b.{0,45}\b(?:ai|artificial intelligence)\b',title,re.I))


def section_for(url):
    parts=[part.casefold() for part in urlparse(url or '').path.split('/') if part]
    return parts[0] if parts else None


def _decision(outcome,rule,terms=()):
    return {'outcome':outcome,'rule':rule,'matched_terms':_unique(terms)}


def topic_decision(title,url='',source=None):
    """Return an outcome and the unique keyword/section rule that produced it."""
    source=source or {};title=title or '';section=section_for(url)
    strong=_has(title,STRONG_TERMS)+_has(title,NORWEGIAN_STEMS)
    strong=_unique(strong)
    weak=_has(title,WEAK_TERMS)
    off=_has(title,OFF_TOPIC_TERMS)
    tech=_tech_product(title)
    finance=_has(title,FINANCIAL_TECH_TERMS)
    is_e24=source.get('id')=='e24' or 'e24.no' in (url or '')

    if is_e24 and section in E24_DENIED:
        return _decision('DROP','E24 denied section: '+section)
    if tech and not finance:
        return _decision('LOW_CONFIDENCE','technology product story lacks a separate financial signal'+(': '+', '.join(strong) if strong else ''),strong)
    # Financial context can soften an off-topic match, never make it high
    # confidence. Names alone are not topics.
    if off and (strong or finance):
        return _decision('LOW_CONFIDENCE','off-topic term overridden by economic signal: '+', '.join(_unique(off+strong+finance)),off+strong+finance)
    if off:
        return _decision('DROP','off-topic topic: '+', '.join(off),off)

    if strong:
        return _decision('KEEP','strong financial keyword: '+', '.join(strong),strong+weak)
    if weak and is_e24:
        return _decision('LOW_CONFIDENCE','weak keyword plus E24 section context: '+', '.join(weak),weak)
    if is_e24 and section in E24_KEEP_DEFAULT:
        return _decision('LOW_CONFIDENCE','E24 section default only, without a confirming keyword: '+section,weak)
    if is_e24 and section in E24_LOW_DEFAULT:
        return _decision('LOW_CONFIDENCE','E24 low-confidence section default: '+section,weak)
    if is_e24:
        return _decision('LOW_CONFIDENCE','E24 section not in configured section defaults',weak)
    context=_has(title,WEAK_CONTEXT_TERMS)
    if context:
        return _decision('LOW_CONFIDENCE','weak business/geopolitical signal: '+', '.join(context),context+weak)
    return _decision('DROP','no financial topic or approved section signal',weak)


def financial_topic(title):
    """Compatibility predicate: only confidently KEEP outcomes qualify."""
    return topic_decision(title)['outcome']=='KEEP'
