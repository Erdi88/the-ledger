"""Value-investing rules from the three books, applied as transparent checks beside the statistical model.

Graham: margin of safety, earnings stability, modest valuation, conservative debt.
Munger: invert (list what could go wrong first), avoid stupidity, stay inside the circle of competence.
Thorndike's Outsiders: capital allocation and per-share free cash flow; shrinking share count with real cash flow.
These labels are stored with each prediction so the scorecard can later test whether they carried any information.
"""
import pandas as pd

def _v(row, k):
    x = row.get(k)
    return None if x is None or pd.isna(x) else float(x)

def margin_of_safety(row):
    """Graham-style defensive screen -> (passed|None, reasons). Norwegian names have no fundamentals here."""
    ey, pb, d2e, py = _v(row, 'earn_yield'), _v(row, 'pb'), _v(row, 'debt_to_equity'), _v(row, 'profit_years')
    if ey is None and pb is None:
        return None, ['no fundamentals available (price-only name)']
    checks = []
    if ey is not None: checks.append(('earnings yield >= 4% (P/E <= 25)', ey >= 0.04))
    if pb is not None: checks.append(('price/book <= 6', pb <= 6))
    if d2e is not None: checks.append(('debt/equity <= 1.5', d2e <= 1.5))
    if py is not None: checks.append(('profitable in most of last 5 years', py >= 4))
    return all(ok for _, ok in checks), [f"{'PASS' if ok else 'FAIL'}: {n}" for n, ok in checks]

def red_flags(row):
    """Munger's inversion: what would make us look stupid? Any flag blocks an UP call."""
    flags = []
    dd, fy, sc, d2e, vol = _v(row, 'dd_252'), _v(row, 'fcf_yield'), _v(row, 'share_change'), _v(row, 'debt_to_equity'), _v(row, 'vol_63')
    if dd is not None and dd < -0.40: flags.append('down more than 40% from 1y high (falling knife)')
    if fy is not None and fy < 0: flags.append('negative free cash flow')
    if sc is not None and sc > 0.03: flags.append('share count up >3% (dilution)')
    if d2e is not None and d2e > 2.5: flags.append('high leverage (debt/equity > 2.5)')
    if vol is not None and vol > 0.60: flags.append('annual volatility above 60%')
    return flags

def capital_allocation(row):
    sc, fy = _v(row, 'share_change'), _v(row, 'fcf_yield')
    if sc is None or fy is None: return None
    return 'shareholder-friendly' if (sc < -0.005 and fy > 0.03) else ('neutral' if sc <= 0.01 else 'dilutive')
