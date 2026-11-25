# CNBC and E24 title filter review

**Headline evidence: LIVE-VERIFIED** in the returned `live_probe_results.json` (user-machine probe, 2026-10-13). **Classification: TESTED-OFFLINE** using the unchanged title filter. This report does not claim collection under the revised code. No article text is included.

Rules used, in order: (1) if any `OFF_TOPIC` expression matches, DROP and list those matches; (2) otherwise if `FINANCE` matches, KEEP and list the finance term(s); (3) otherwise DROP because no finance keyword matched. The source filter remains unchanged.

## CNBC — 30 headlines

|Decision|Headline (original)|Applied rule|
|---|---|---|
|KEEP|IMF warns bond yields could see a 'disorderly' spike as debt, inflation risks worsen|FINANCE matched: IMF, bond, debt, inflation|
|KEEP|Oil prices fall as traders assess Russian diesel supply prospects and Saudi-Houthi conflict|FINANCE matched: Oil|
|KEEP|SK Hynix, SoftBank shares plunge as tech stocks in Asia track Wall Street chip sell-off|FINANCE matched: shares, stocks|
|KEEP|Six Flags shares plunge after-hours following report of deadly roller coaster incident|FINANCE matched: shares|
|DROP|How Red Bull's F1 team is using AI to make split-second decisions for Max Verstappen|OFF_TOPIC matched: F1|
|DROP|Trump defends Russia diesel deal after bipartisan pushback: 'I made the right choice'|OFF_TOPIC matched: Trump|
|DROP|Rep. Ilhan Omar blasts federal criminal raid on home: 'I will not be silenced'|No FINANCE keyword matched|
|KEEP|'Boring is not bad': CEO of Southeast Asia's largest bank pitches Singapore as a haven amid global turmoil|FINANCE matched: bank|
|DROP|Elon Musk gives $276 million to Republican groups, becomes biggest known 2026 midterm donor|OFF_TOPIC matched: Republican, midterm|
|DROP|CNBC's The China Connection newsletter: How a gold-buying spree helps the yuan go global|No FINANCE keyword matched|
|DROP|FAA warns U.S. airlines of safety risks over Saudi Arabia after attacks|No FINANCE keyword matched|
|DROP|Delta delays debut of Saudi Arabia service until March after Riyadh airport attacks|No FINANCE keyword matched|
|KEEP|Singapore PM Wong rejects weaker currency as shortcut to competitiveness|FINANCE matched: currency|
|DROP|Trump 'not happy' with Kimberly Guilfoyle, weighs firing her as ambassador to Greece|OFF_TOPIC matched: Trump, ambassador|
|KEEP|Earnings beats are now the norm. What the stock market needs to keep rallying|FINANCE matched: Earnings, stock, market|
|KEEP|A massive trade just happened in surging shares of Snap|FINANCE matched: trade, shares|
|DROP|Meta debuts Muse Wonder AI model in latest test of users' willingness to pay|No FINANCE keyword matched|
|DROP|Here's a calculator to explain why Cramer always stays invested. Plug in your own numbers, too|No FINANCE keyword matched|
|KEEP|Higher rates could be needed to avoid 'inflationary mindset' taking hold, says Fed's Hammack|FINANCE matched: rates, Fed|
|DROP|GM CEO: We're making leaps and bounds toward 'eyes-off, hands-off' driving|No FINANCE keyword matched|
|KEEP|World Bank jobs council urges 'crisis-era' employment support measures as IMF warns of AI ‘tsunami’|FINANCE matched: Bank, employment, IMF|
|KEEP|IonQ to acquire cybersecurity firm Elisity in an all-stock deal for up to $1.3 billion|FINANCE matched: stock|
|KEEP|India’s retail inflation jumps to 5.54% in September, above estimates|FINANCE matched: inflation|
|DROP|Starbucks says it is not buying Chipotle after takeover speculation|No FINANCE keyword matched|
|KEEP|UnitedHealth shares are doing something unusual ahead of earnings|FINANCE matched: shares, earnings|
|DROP|McDonald's is leaning into chicken and drinks to grow. New data shows it could be a tough task|No FINANCE keyword matched|
|DROP|Why older Americans' wealth may be helping keep consumer spending strong|No FINANCE keyword matched|
|DROP|Microsoft to rely more on homegrown AI chips, reducing dependence on Nvidia|No FINANCE keyword matched|
|KEEP|Banks are set to report this week. Here's what the options market expects|FINANCE matched: Banks, options, market|
|DROP|Saudi Arabia says drones and missiles still targeting kingdom as Iran-backed Houthis step up attacks|No FINANCE keyword matched|

Count: 14 kept; 16 dropped.

## E24 — 39 headlines

|Decision|Headline (original)|Applied rule|
|---|---|---|
|DROP|Inntektshopp for ABG|No FINANCE keyword matched|
|DROP|Nel varsler Rheinmetall-samarbeid|No FINANCE keyword matched|
|DROP|Kraftig tekfall i Asia|No FINANCE keyword matched|
|DROP|Snart kan vi dø av lungebetennelse igjen|OFF_TOPIC matched: lungebetennelse|
|DROP|Konsulent-toppene: Slik får du drømmejobben|OFF_TOPIC matched: drømmejobben|
|DROP|– NVE svarer bare «bla bla bla»|No FINANCE keyword matched|
|DROP|Vil ikke godta Posten-kutt: – Brutalt|No FINANCE keyword matched|
|DROP|Regnskapsfører mener gründere kan spare tusenvis|No FINANCE keyword matched|
|DROP|Kutter prisen for Geilo-luksus med 4 mill.|No FINANCE keyword matched|
|DROP|Må jeg skrive jobbsøknad for maskiner?|OFF_TOPIC matched: jobbsøknad|
|DROP|Spytter inn 2,6 milliarder i mellomvalget|OFF_TOPIC matched: mellomvalget|
|DROP|DN: Anette Ringnes står frem som Epstein-varsler|OFF_TOPIC matched: Epstein|
|DROP|Mark Zuckerberg: Meta har tatt igjen AI-rivaler med ny modell|No FINANCE keyword matched|
|DROP|Tviler på Trumps diesel-avtale: – Hjelper veldig lite|No FINANCE keyword matched|
|KEEP|Mote-smell i Kina for børstaper LVMH|FINANCE matched: børstaper|
|DROP|Det er én løsning|No FINANCE keyword matched|
|KEEP|Burrito-aksje falt på Wall Street etter Starbucks-nei|FINANCE matched: aksje|
|DROP|Sjekk din kommune eller bydel: Her stiger boligprisene mest og minst|No FINANCE keyword matched|
|DROP|Google må stanse datasenterbygging: – Områdene er redusert til sand|No FINANCE keyword matched|
|DROP|Robert E. Hall og Michael Woodford får nobelprisen i økonomi|No FINANCE keyword matched|
|DROP|Shippingvinner: – Eksepsjonelt|No FINANCE keyword matched|
|DROP|Fastlåst i Midtøsten: – Kan nok vedvare et halvt år til|No FINANCE keyword matched|
|DROP|VGs sjefredaktør Gard Steiro (50) gir seg|OFF_TOPIC matched: sjefredaktør|
|DROP|Milliardveddemål mot bilaksje|No FINANCE keyword matched|
|DROP|– Den største konkurranse­rettssaken noensinne|No FINANCE keyword matched|
|DROP|Sara Midtgaard slutter i Nordea Markets|No FINANCE keyword matched|
|KEEP|Frontline til topps på Oslo Børs|FINANCE matched: Børs|
|DROP|Telia nedbemanner – kutter 150 stillinger i Norge|No FINANCE keyword matched|
|DROP|Senatorer mot Trumps avtale: – Bryter loven|No FINANCE keyword matched|
|KEEP|Børsfrykt: – Risikoen har økt betraktelig|FINANCE matched: Børsfrykt|
|KEEP|Reagerer på rentegrep: – De gir kundene fingeren|FINANCE matched: rentegrep|
|DROP|Resultatrush: – Kommer til å levere bra|No FINANCE keyword matched|
|DROP|Dagligvare­kjedenes advokater: – En klar overmakt|No FINANCE keyword matched|
|DROP|– Kan trekke i retning av høyere prisvekst|No FINANCE keyword matched|
|DROP|Trump: Enige om stans i energi-angrep|OFF_TOPIC matched: Trump|
|DROP|IEA: Ber land vurdere nye diesel-slipp|No FINANCE keyword matched|
|DROP|Ukrainsk dagligvaretopp: – Ha litt kontanter|No FINANCE keyword matched|
|DROP|Nå kan jobbsøknaden din bli vurdert av en maskin|No FINANCE keyword matched|
|DROP|Vil ha 1000 nye trainee-stillinger i statsbudsjettet|No FINANCE keyword matched|

Count: 5 kept; 34 dropped.
