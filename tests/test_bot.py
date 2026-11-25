import json, tempfile, unittest, pathlib, datetime as dt
try:
    import numpy as np, pandas as pd
    from bot import features, principles, prices, resolve, store, report
except ImportError:                         # numpy/pandas are only needed for the bot
    np = None

@unittest.skipIf(np is None, 'bot dependencies not installed')
class BotTests(unittest.TestCase):
    def test_parse_chart_uses_adjusted_close_and_skips_gaps(self):
        payload = {'chart': {'result': [{'timestamp': [1700000000, 1700086400, 1700172800],
            'indicators': {'quote': [{'close': [10, None, 12], 'volume': [1, 2, 3]}], 'adjclose': [{'adjclose': [9, None, 11]}]}}]}}
        rows = prices.parse_chart(payload)
        self.assertEqual([r[2] for r in rows], [9, 11])

    def test_fundamentals_not_visible_before_filing_date(self):
        idx = pd.bdate_range('2020-01-01', periods=700)
        s = pd.Series(100.0, index=idx)
        fund = pd.DataFrame({'end': [pd.Timestamp('2019-12-31')], 'filed': [pd.Timestamp('2020-06-01')],
                             'eps': [10.0], 'shares': [1.0], 'equity': [50.0], 'net_income': [10.0]})
        f = features.fundamental_features(s, fund)
        self.assertTrue(f.loc[:'2020-05-29', 'earn_yield'].isna().all())      # nothing known yet
        self.assertAlmostEqual(f.loc['2020-06-02', 'earn_yield'], 0.10)
        self.assertTrue(f.iloc[-1:]['earn_yield'].isna().all())               # >550 days old counts as stale

    def test_targets_look_forward_features_look_back(self):
        idx = pd.bdate_range('2020-01-01', periods=400)
        s = pd.Series(np.linspace(100, 200, 400), index=idx)
        u = {'stocks': [{'t': 'X', 'region': 'US'}], 'benchmarks': {'US': 'B'}, 'macro': {}}
        panel = features.build_panel(u, {'X': s}, {'US': s}, {}, {}, True)
        row = panel.iloc[100]
        self.assertAlmostEqual(row['mom_21'], s.iloc[100] / s.iloc[79] - 1)
        self.assertAlmostEqual(row['ret_1m'], s.iloc[121] / s.iloc[100] - 1)

    def test_red_flags_and_margin_of_safety(self):
        bad = pd.Series({'dd_252': -0.5, 'fcf_yield': -0.01, 'share_change': 0.05, 'debt_to_equity': 3.0, 'vol_63': 0.7})
        self.assertEqual(len(principles.red_flags(bad)), 5)
        self.assertIsNone(principles.margin_of_safety(pd.Series({}))[0])
        ok = pd.Series({'earn_yield': 0.06, 'pb': 2.0, 'debt_to_equity': 0.5, 'profit_years': 5})
        self.assertTrue(principles.margin_of_safety(ok)[0])

    def test_resolution_grades_calls_and_never_resolves_early(self):
        with tempfile.TemporaryDirectory() as d:
            store.PRED, store.OUT = pathlib.Path(d) / 'p.jsonl', pathlib.Path(d) / 'o.jsonl'
            store.append(store.PRED, [
                {'id': 'a', 'made_at': '2024-01-02', 'ticker': 'X', 'region': 'US', 'horizon': '1m', 'due_date': '2024-02-01',
                 'price': 100.0, 'p_up': 0.7, 'call': 'UP'},
                {'id': 'b', 'made_at': '2024-01-02', 'ticker': 'X', 'region': 'US', 'horizon': '1m', 'due_date': '2030-01-01',
                 'price': 100.0, 'p_up': 0.7, 'call': 'UP'},
                {'id': 'c', 'made_at': '2024-01-02', 'ticker': 'X', 'region': 'US', 'horizon': '1m', 'due_date': '2024-02-01',
                 'price': 100.0, 'p_up': 0.5, 'call': 'ABSTAIN'}])
            s = pd.Series([100.0, 90.0], index=pd.to_datetime(['2024-01-02', '2024-02-01']))
            out = {o['id']: o for o in resolve.resolve({'X': s}, {'US': s})}
            self.assertEqual(set(out), {'a', 'c'})                         # 'b' is in the future
            self.assertFalse(out['a']['correct'])                          # called UP, fell 10%
            self.assertIsNone(out['c']['correct'])                         # abstentions are never scored as right
            store.append(store.OUT, list(out.values()))
            self.assertEqual(resolve.resolve({'X': s}, {'US': s}), [])     # idempotent
            sc = report.scorecard()
            self.assertEqual(sc['totals'], {'predictions': 3, 'resolved': 2, 'pending': 1})
            self.assertEqual(sc['by_horizon']['1m']['hit_rate'], 0.0)

if __name__ == '__main__':
    unittest.main()
