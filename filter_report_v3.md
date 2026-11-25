# Topic filter v3 — probe sample review

**Source evidence: LIVE-VERIFIED** in returned `live_probe_results.json` (2026-10-13). **Reclassification: TESTED-OFFLINE** with the current local filter. This is headline and URL metadata review; no live collection was run and no fixtures were used.

The v3 filter returns KEEP, LOW_CONFIDENCE, or DROP. English terms of five characters or fewer require whole-word matches; listed Norwegian stems match within compounds. E24 section defaults are confidence-capped without a keyword. Tech product news requires a separate financial term to exceed LOW_CONFIDENCE.

## Diff against v2

Every row shows the v2 outcome followed by the v3 outcome, plus the v3 rule. The probe sample inputs were not edited.

## CNBC — 30 probe samples

|v2 → v3|Headline|v3 rule|
|---|---|---|
|KEEP → KEEP|IMF warns bond yields could see a 'disorderly' spike as debt, inflation risks worsen|strong financial keyword: inflation, bond, yields, imf|
|KEEP → KEEP|Oil prices fall as traders assess Russian diesel supply prospects and Saudi-Houthi conflict|strong financial keyword: diesel, oil|
|KEEP → KEEP|SK Hynix, SoftBank shares plunge as tech stocks in Asia track Wall Street chip sell-off|strong financial keyword: chip, shares, stocks|
|KEEP → KEEP|Six Flags shares plunge after-hours following report of deadly roller coaster incident|strong financial keyword: shares|
|DROP → DROP|How Red Bull's F1 team is using AI to make split-second decisions for Max Verstappen|off-topic topic: f1|
|KEEP → KEEP|Trump defends Russia diesel deal after bipartisan pushback: 'I made the right choice'|strong financial keyword: diesel, deal|
|DROP → DROP|Rep. Ilhan Omar blasts federal criminal raid on home: 'I will not be silenced'|off-topic topic: raid|
|KEEP → KEEP|'Boring is not bad': CEO of Southeast Asia's largest bank pitches Singapore as a haven amid global turmoil|strong financial keyword: bank|
|DROP → DROP|Elon Musk gives $276 million to Republican groups, becomes biggest known 2026 midterm donor|off-topic topic: midterm, donor|
|KEEP → KEEP|CNBC's The China Connection newsletter: How a gold-buying spree helps the yuan go global|strong financial keyword: gold, yuan|
|DROP → DROP|FAA warns U.S. airlines of safety risks over Saudi Arabia after attacks|off-topic topic: airlines|
|DROP → DROP|Delta delays debut of Saudi Arabia service until March after Riyadh airport attacks|off-topic topic: delays debut, airport attacks|
|KEEP → KEEP|Singapore PM Wong rejects weaker currency as shortcut to competitiveness|strong financial keyword: currency|
|DROP → DROP|Trump 'not happy' with Kimberly Guilfoyle, weighs firing her as ambassador to Greece|off-topic topic: ambassador|
|KEEP → KEEP|Earnings beats are now the norm. What the stock market needs to keep rallying|strong financial keyword: earnings, stock|
|KEEP → KEEP|A massive trade just happened in surging shares of Snap|strong financial keyword: shares|
|LOW_CONFIDENCE → LOW_CONFIDENCE|Meta debuts Muse Wonder AI model in latest test of users' willingness to pay|technology product story lacks a separate financial signal|
|DROP → DROP|Here's a calculator to explain why Cramer always stays invested. Plug in your own numbers, too|off-topic topic: calculator|
|KEEP → KEEP|Higher rates could be needed to avoid 'inflationary mindset' taking hold, says Fed's Hammack|strong financial keyword: fed, rates|
|DROP → DROP|GM CEO: We're making leaps and bounds toward 'eyes-off, hands-off' driving|no financial topic or approved section signal|
|KEEP → KEEP|World Bank jobs council urges 'crisis-era' employment support measures as IMF warns of AI ‘tsunami’|strong financial keyword: bank, imf|
|KEEP → KEEP|IonQ to acquire cybersecurity firm Elisity in an all-stock deal for up to $1.3 billion|strong financial keyword: acquire, stock, deal|
|KEEP → KEEP|India’s retail inflation jumps to 5.54% in September, above estimates|strong financial keyword: inflation|
|KEEP → KEEP|Starbucks says it is not buying Chipotle after takeover speculation|strong financial keyword: takeover|
|KEEP → KEEP|UnitedHealth shares are doing something unusual ahead of earnings|strong financial keyword: earnings, shares|
|LOW_CONFIDENCE → LOW_CONFIDENCE|McDonald's is leaning into chicken and drinks to grow. New data shows it could be a tough task|weak business/geopolitical signal: mcdonald|
|KEEP → KEEP|Why older Americans' wealth may be helping keep consumer spending strong|strong financial keyword: wealth, spending, consumer spending|
|KEEP → LOW_CONFIDENCE|Microsoft to rely more on homegrown AI chips, reducing dependence on Nvidia|technology product story lacks a separate financial signal: nvidia, chips|
|KEEP → KEEP|Banks are set to report this week. Here's what the options market expects|strong financial keyword: banks|
|LOW_CONFIDENCE → LOW_CONFIDENCE|Saudi Arabia says drones and missiles still targeting kingdom as Iran-backed Houthis step up attacks|weak business/geopolitical signal: saudi, attacks|

Counts: 18 KEEP, 4 LOW_CONFIDENCE, 8 DROP.

## E24 — 39 probe samples

|v2 → v3|Headline|v3 rule|
|---|---|---|
|KEEP → KEEP|Inntektshopp for ABG|strong financial keyword: inntektshopp|
|KEEP → KEEP|Nel varsler Rheinmetall-samarbeid|strong financial keyword: samarbeid|
|KEEP → KEEP|Kraftig tekfall i Asia|strong financial keyword: tekfall|
|DROP → DROP|Snart kan vi dø av lungebetennelse igjen|off-topic topic: lungebetennelse|
|DROP → DROP|Konsulent-toppene: Slik får du drømmejobben|E24 denied section: karriere-og-ledelse|
|KEEP → LOW_CONFIDENCE|– NVE svarer bare «bla bla bla»|E24 low-confidence section default: naeringsliv|
|KEEP → LOW_CONFIDENCE|Vil ikke godta Posten-kutt: – Brutalt|E24 section default only, without a confirming keyword: norsk-oekonomi|
|KEEP → KEEP|Regnskapsfører mener gründere kan spare tusenvis|strong financial keyword: regnskapsfører|
|KEEP → LOW_CONFIDENCE|Kutter prisen for Geilo-luksus med 4 mill.|E24 low-confidence section default: naeringsliv|
|DROP → DROP|Må jeg skrive jobbsøknad for maskiner?|E24 denied section: karriere-og-ledelse|
|DROP → DROP|Spytter inn 2,6 milliarder i mellomvalget|off-topic topic: mellomvalget|
|DROP → DROP|DN: Anette Ringnes står frem som Epstein-varsler|off-topic topic: epstein|
|KEEP → LOW_CONFIDENCE|Mark Zuckerberg: Meta har tatt igjen AI-rivaler med ny modell|technology product story lacks a separate financial signal|
|KEEP → KEEP|Tviler på Trumps diesel-avtale: – Hjelper veldig lite|strong financial keyword: diesel|
|KEEP → KEEP|Mote-smell i Kina for børstaper LVMH|strong financial keyword: børs|
|LOW_CONFIDENCE → LOW_CONFIDENCE|Det er én løsning|E24 section not in configured section defaults|
|KEEP → KEEP|Burrito-aksje falt på Wall Street etter Starbucks-nei|strong financial keyword: aksj|
|KEEP → KEEP|Sjekk din kommune eller bydel: Her stiger boligprisene mest og minst|strong financial keyword: bolig|
|KEEP → KEEP|Google må stanse datasenterbygging: – Områdene er redusert til sand|strong financial keyword: datasenter|
|KEEP → KEEP|Robert E. Hall og Michael Woodford får nobelprisen i økonomi|strong financial keyword: økonomi, økonom|
|KEEP → KEEP|Shippingvinner: – Eksepsjonelt|strong financial keyword: shipping|
|LOW_CONFIDENCE → LOW_CONFIDENCE|Fastlåst i Midtøsten: – Kan nok vedvare et halvt år til|weak keyword plus E24 section context: midtøsten|
|DROP → DROP|VGs sjefredaktør Gard Steiro (50) gir seg|off-topic topic: sjefredaktør|
|KEEP → KEEP|Milliardveddemål mot bilaksje|strong financial keyword: aksj|
|KEEP → LOW_CONFIDENCE|– Den største konkurranse­rettssaken noensinne|E24 low-confidence section default: naeringsliv|
|KEEP → LOW_CONFIDENCE|Sara Midtgaard slutter i Nordea Markets|weak keyword plus E24 section context: markets|
|KEEP → KEEP|Frontline til topps på Oslo Børs|strong financial keyword: børs|
|KEEP → KEEP|Telia nedbemanner – kutter 150 stillinger i Norge|strong financial keyword: nedbemann|
|DROP → LOW_CONFIDENCE|Senatorer mot Trumps avtale: – Bryter loven|E24 section default only, without a confirming keyword: internasjonal-oekonomi|
|KEEP → KEEP|Børsfrykt: – Risikoen har økt betraktelig|strong financial keyword: børs|
|KEEP → KEEP|Reagerer på rentegrep: – De gir kundene fingeren|strong financial keyword: rente|
|KEEP → KEEP|Resultatrush: – Kommer til å levere bra|strong financial keyword: resultat|
|KEEP → LOW_CONFIDENCE|Dagligvare­kjedenes advokater: – En klar overmakt|E24 low-confidence section default: naeringsliv|
|KEEP → KEEP|– Kan trekke i retning av høyere prisvekst|strong financial keyword: prisvekst|
|LOW_CONFIDENCE → LOW_CONFIDENCE|Trump: Enige om stans i energi-angrep|weak keyword plus E24 section context: angrep|
|KEEP → KEEP|IEA: Ber land vurdere nye diesel-slipp|strong financial keyword: diesel|
|KEEP → LOW_CONFIDENCE|Ukrainsk dagligvaretopp: – Ha litt kontanter|E24 section default only, without a confirming keyword: internasjonal-oekonomi|
|DROP → DROP|Nå kan jobbsøknaden din bli vurdert av en maskin|E24 denied section: karriere-og-ledelse|
|DROP → DROP|Vil ha 1000 nye trainee-stillinger i statsbudsjettet|off-topic topic: trainee-stillinger|

Counts: 19 KEEP, 12 LOW_CONFIDENCE, 8 DROP.

## FT — 10 probe samples

|v2 → v3|Headline|v3 rule|
|---|---|---|
|KEEP → KEEP|Top economies heading for biggest budget deficits since Covid, IMF warns|strong financial keyword: imf|
|DROP → DROP|Asia warned over zombie companies|no financial topic or approved section signal|
|DROP → DROP|The election supercycle set to drag Europe right|no financial topic or approved section signal|
|DROP → DROP|Why Trump is going for Zelenskyy’s jugular|no financial topic or approved section signal|
|DROP → DROP|Who’s really hiring you — HR or cyber security?|no financial topic or approved section signal|
|KEEP → KEEP|Chip stocks slide in wake of ‘casino’ comment by Broadcom boss|strong financial keyword: chip, stocks|
|DROP → LOW_CONFIDENCE|Zuckerberg says Meta has reached AI ‘frontier’|weak business/geopolitical signal: ai|
|KEEP → KEEP|Investors brave US Treasury rout to lock in highest yields in decades|strong financial keyword: yields|
|LOW_CONFIDENCE → LOW_CONFIDENCE|Houthi assault on Saudi airports strikes at MBS’s economic vision|weak business/geopolitical signal: saudi|
|KEEP → LOW_CONFIDENCE|China resorts to Nvidia gaming chips in search for AI firepower|technology product story lacks a separate financial signal: nvidia, chips|

Counts: 3 KEEP, 3 LOW_CONFIDENCE, 4 DROP.
