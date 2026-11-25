# How the bot thinks (and where it admits it does not)

The bot's job is narrow: for a fixed list of large stocks, give a probability that the price is higher in
1 and 3 months, write that guess down **before** the outcome, and grade itself afterwards. It never places orders.

## Ideas taken from the three books in `Imma get rich mami`
| Idea | Source | What the code does |
|---|---|---|
| Mr. Market is moody; price is not value | Graham, *The Intelligent Investor* | Yields (earnings, FCF, dividend) and price/book are recomputed daily against the last *filed* accounts |
| Margin of safety | Graham | `principles.margin_of_safety`: P/E, P/B, debt, 4-of-5 profitable years. Stored per prediction; the scorecard tests whether passing it actually mattered |
| Circle of competence | Munger, *Poor Charlie's Almanack* | A short fixed universe (`bot/universe.json`); names are added deliberately |
| Invert, always invert | Munger | `principles.red_flags`: falling knife, negative FCF, dilution, leverage, extreme volatility. An UP call with a flag becomes ABSTAIN |
| Avoid stupidity before seeking brilliance | Munger | Abstaining is a first-class answer (P between 0.43 and 0.57); abstentions are never counted as wins |
| Capital allocation is the CEO's real job; per-share FCF matters | Thorndike, *The Outsiders* | Share-count change, buyback yield, FCF per share, ROE as features and a `capital_allocation` label |
| Be honest about base rates | Munger / Graham | The model must beat "stocks usually go up". The baseline is always printed next to it |

## Honesty rules
- **Walk-forward testing only.** Each test year is predicted by a model trained on data that ended a full horizon earlier.
- **Point-in-time fundamentals.** A number is usable only from the date it was filed with the SEC.
- **Edge is claimed only when proven**: out-of-sample AUC >= 0.53 and a Brier score better than the base rate, at every horizon.
- **Append-only log.** `bot_data/predictions.jsonl` is only ever appended to; outcomes go in `outcomes.jsonl`. Git history proves nothing was edited.

## Known limits (v1)
- Norwegian stocks have prices and macro only: no free, structured fundamentals feed was found. This is the main gap.
- Prices come from Yahoo Finance's unofficial public endpoint. Fine for personal research, not a guaranteed feed.
- Honest first result: **no demonstrated edge** (AUC about 0.51). Daily price patterns plus basic fundamentals on 30 large stocks is a weak signal.
  The useful part today is the measurement machinery. Better inputs are the next step: earnings surprises, news from official
  sources (the newspaper side of this repo), analyst revisions, Oslo Børs announcements.
- Not investment advice. Do not trade money on this without independent evidence.
