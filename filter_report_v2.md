# Topic filter v2 — probe sample review

**Source evidence: LIVE-VERIFIED** in returned `live_probe_results.json` (2026-10-13). **Reclassification: TESTED-OFFLINE** with the current local filter. These are headline and URL metadata only; no live collection was run and no fixtures were used.

The filter returns KEEP, LOW_CONFIDENCE, or DROP. E24 section is the default when present. A LOW_CONFIDENCE item may appear in the full edition but is excluded from Top 5. Dropped records are preserved in `data/filtered_out.json` with the applied rule.

## Diff against v1

v1 had only KEEP/DROP and covered CNBC and E24; FT was not included. The table shows the previous decision and current result for each probe sample.

## CNBC — 30 probe samples

|v1 → v2|Headline|v2 rule|
|---|---|---|
|KEEP → KEEP|IMF warns bond yields could see a 'disorderly' spike as debt, inflation risks worsen|strong economic keyword: inflation, bond, yield, imf, yield|
|KEEP → KEEP|Oil prices fall as traders assess Russian diesel supply prospects and Saudi-Houthi conflict|strong economic keyword: diesel, oil, trade, price, diesel|
|KEEP → KEEP|SK Hynix, SoftBank shares plunge as tech stocks in Asia track Wall Street chip sell-off|strong economic keyword: chip, bank, shares, stock|
|KEEP → KEEP|Six Flags shares plunge after-hours following report of deadly roller coaster incident|strong economic keyword: shares|
|DROP → DROP|How Red Bull's F1 team is using AI to make split-second decisions for Max Verstappen|off-topic topic: f1|
|DROP → KEEP|Trump defends Russia diesel deal after bipartisan pushback: 'I made the right choice'|strong economic keyword: diesel, diesel|
|DROP → DROP|Rep. Ilhan Omar blasts federal criminal raid on home: 'I will not be silenced'|off-topic topic: raid|
|KEEP → KEEP|'Boring is not bad': CEO of Southeast Asia's largest bank pitches Singapore as a haven amid global turmoil|strong economic keyword: oil, bank|
|DROP → DROP|Elon Musk gives $276 million to Republican groups, becomes biggest known 2026 midterm donor|off-topic topic: midterm, donor|
|DROP → KEEP|CNBC's The China Connection newsletter: How a gold-buying spree helps the yuan go global|strong economic keyword: gold, yuan|
|DROP → DROP|FAA warns U.S. airlines of safety risks over Saudi Arabia after attacks|off-topic topic: airlines|
|DROP → DROP|Delta delays debut of Saudi Arabia service until March after Riyadh airport attacks|off-topic topic: delays debut, airport attacks|
|KEEP → KEEP|Singapore PM Wong rejects weaker currency as shortcut to competitiveness|strong economic keyword: currency|
|DROP → DROP|Trump 'not happy' with Kimberly Guilfoyle, weighs firing her as ambassador to Greece|off-topic topic: ambassador|
|KEEP → KEEP|Earnings beats are now the norm. What the stock market needs to keep rallying|strong economic keyword: earnings, market, stock|
|KEEP → KEEP|A massive trade just happened in surging shares of Snap|strong economic keyword: shares, trade|
|DROP → LOW_CONFIDENCE|Meta debuts Muse Wonder AI model in latest test of users' willingness to pay|weak business/geopolitical signal: ai model|
|DROP → DROP|Here's a calculator to explain why Cramer always stays invested. Plug in your own numbers, too|off-topic topic: calculator|
|KEEP → KEEP|Higher rates could be needed to avoid 'inflationary mindset' taking hold, says Fed's Hammack|strong economic keyword: fed, rates, inflation, eia, sec, rates|
|DROP → DROP|GM CEO: We're making leaps and bounds toward 'eyes-off, hands-off' driving|no financial topic or approved section signal|
|KEEP → KEEP|World Bank jobs council urges 'crisis-era' employment support measures as IMF warns of AI ‘tsunami’|strong economic keyword: bank, imf|
|KEEP → KEEP|IonQ to acquire cybersecurity firm Elisity in an all-stock deal for up to $1.3 billion|strong economic keyword: acquire, stock|
|KEEP → KEEP|India’s retail inflation jumps to 5.54% in September, above estimates|strong economic keyword: inflation, retail|
|DROP → KEEP|Starbucks says it is not buying Chipotle after takeover speculation|strong economic keyword: takeover, chip|
|KEEP → KEEP|UnitedHealth shares are doing something unusual ahead of earnings|strong economic keyword: earnings, shares|
|DROP → LOW_CONFIDENCE|McDonald's is leaning into chicken and drinks to grow. New data shows it could be a tough task|weak business/geopolitical signal: mcdonald|
|DROP → KEEP|Why older Americans' wealth may be helping keep consumer spending strong|strong economic keyword: consumer spending, wealth, spending|
|DROP → KEEP|Microsoft to rely more on homegrown AI chips, reducing dependence on Nvidia|strong economic keyword: nvidia, chip|
|KEEP → KEEP|Banks are set to report this week. Here's what the options market expects|strong economic keyword: bank, market|
|DROP → LOW_CONFIDENCE|Saudi Arabia says drones and missiles still targeting kingdom as Iran-backed Houthis step up attacks|weak business/geopolitical signal: saudi, attacks|

Counts: 19 KEEP, 3 LOW_CONFIDENCE, 8 DROP.

## E24 — 39 probe samples

|v1 → v2|Headline|v2 rule|
|---|---|---|
|DROP → KEEP|Inntektshopp for ABG|strong economic keyword: inntekt|
|DROP → KEEP|Nel varsler Rheinmetall-samarbeid|E24 allowed section default: boers-og-finans|
|DROP → KEEP|Kraftig tekfall i Asia|strong economic keyword: tekfall|
|DROP → DROP|Snart kan vi dø av lungebetennelse igjen|off-topic topic: lungebetennelse|
|DROP → DROP|Konsulent-toppene: Slik får du drømmejobben|off-topic topic: drømmejobb|
|DROP → KEEP|– NVE svarer bare «bla bla bla»|E24 allowed section default: naeringsliv|
|DROP → KEEP|Vil ikke godta Posten-kutt: – Brutalt|E24 allowed section default: norsk-oekonomi|
|DROP → KEEP|Regnskapsfører mener gründere kan spare tusenvis|strong economic keyword: regnskap|
|DROP → KEEP|Kutter prisen for Geilo-luksus med 4 mill.|E24 allowed section default: naeringsliv|
|DROP → DROP|Må jeg skrive jobbsøknad for maskiner?|off-topic topic: jobbsøknad|
|DROP → DROP|Spytter inn 2,6 milliarder i mellomvalget|off-topic topic: mellomvalget|
|DROP → DROP|DN: Anette Ringnes står frem som Epstein-varsler|off-topic topic: epstein|
|DROP → KEEP|Mark Zuckerberg: Meta har tatt igjen AI-rivaler med ny modell|E24 allowed section default: boers-og-finans|
|DROP → KEEP|Tviler på Trumps diesel-avtale: – Hjelper veldig lite|strong economic keyword: diesel, diesel|
|KEEP → KEEP|Mote-smell i Kina for børstaper LVMH|strong economic keyword: børs|
|DROP → LOW_CONFIDENCE|Det er én løsning|E24 section not in approved section list|
|KEEP → KEEP|Burrito-aksje falt på Wall Street etter Starbucks-nei|strong economic keyword: aksj|
|DROP → KEEP|Sjekk din kommune eller bydel: Her stiger boligprisene mest og minst|strong economic keyword: bolig|
|DROP → KEEP|Google må stanse datasenterbygging: – Områdene er redusert til sand|strong economic keyword: datasenter|
|DROP → KEEP|Robert E. Hall og Michael Woodford får nobelprisen i økonomi|strong economic keyword: økonomi, økonom|
|DROP → KEEP|Shippingvinner: – Eksepsjonelt|strong economic keyword: shipping|
|DROP → LOW_CONFIDENCE|Fastlåst i Midtøsten: – Kan nok vedvare et halvt år til|weak business/geopolitical signal: midtøsten|
|DROP → DROP|VGs sjefredaktør Gard Steiro (50) gir seg|off-topic topic: sjefredaktør|
|DROP → KEEP|Milliardveddemål mot bilaksje|strong economic keyword: aksj|
|DROP → KEEP|– Den største konkurranse­rettssaken noensinne|E24 allowed section default: naeringsliv|
|DROP → KEEP|Sara Midtgaard slutter i Nordea Markets|strong economic keyword: market|
|KEEP → KEEP|Frontline til topps på Oslo Børs|strong economic keyword: børs|
|DROP → KEEP|Telia nedbemanner – kutter 150 stillinger i Norge|strong economic keyword: nedbemann|
|DROP → DROP|Senatorer mot Trumps avtale: – Bryter loven|off-topic topic: senator|
|KEEP → KEEP|Børsfrykt: – Risikoen har økt betraktelig|strong economic keyword: børs|
|KEEP → KEEP|Reagerer på rentegrep: – De gir kundene fingeren|strong economic keyword: rente|
|DROP → KEEP|Resultatrush: – Kommer til å levere bra|strong economic keyword: resultat|
|DROP → KEEP|Dagligvare­kjedenes advokater: – En klar overmakt|E24 allowed section default: naeringsliv|
|DROP → KEEP|– Kan trekke i retning av høyere prisvekst|strong economic keyword: prisvekst|
|DROP → LOW_CONFIDENCE|Trump: Enige om stans i energi-angrep|weak business/geopolitical signal: angrep|
|DROP → KEEP|IEA: Ber land vurdere nye diesel-slipp|strong economic keyword: diesel, diesel|
|DROP → KEEP|Ukrainsk dagligvaretopp: – Ha litt kontanter|E24 allowed section default: internasjonal-oekonomi|
|DROP → DROP|Nå kan jobbsøknaden din bli vurdert av en maskin|off-topic topic: jobbsøknad|
|DROP → DROP|Vil ha 1000 nye trainee-stillinger i statsbudsjettet|off-topic topic: trainee-stilling|

Counts: 27 KEEP, 3 LOW_CONFIDENCE, 9 DROP.

## FT — 10 probe samples

|v1 → v2|Headline|v2 rule|
|---|---|---|
|N/A → KEEP|Top economies heading for biggest budget deficits since Covid, IMF warns|strong economic keyword: imf|
|N/A → DROP|Asia warned over zombie companies|no financial topic or approved section signal|
|N/A → DROP|The election supercycle set to drag Europe right|no financial topic or approved section signal|
|N/A → DROP|Why Trump is going for Zelenskyy’s jugular|no financial topic or approved section signal|
|N/A → DROP|Who’s really hiring you — HR or cyber security?|no financial topic or approved section signal|
|N/A → KEEP|Chip stocks slide in wake of ‘casino’ comment by Broadcom boss|strong economic keyword: chip, stock|
|N/A → DROP|Zuckerberg says Meta has reached AI ‘frontier’|no financial topic or approved section signal|
|N/A → KEEP|Investors brave US Treasury rout to lock in highest yields in decades|strong economic keyword: yield, yield|
|N/A → LOW_CONFIDENCE|Houthi assault on Saudi airports strikes at MBS’s economic vision|weak business/geopolitical signal: saudi|
|N/A → KEEP|China resorts to Nvidia gaming chips in search for AI firepower|strong economic keyword: nvidia, chip|

Counts: 4 KEEP, 1 LOW_CONFIDENCE, 5 DROP.
