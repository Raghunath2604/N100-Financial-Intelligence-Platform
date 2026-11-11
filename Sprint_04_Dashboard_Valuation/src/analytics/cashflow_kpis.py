"""Cash-flow KPI and capital-allocation helpers."""
from .ratios import capital_allocation_pattern, safe_divide

def free_cash_flow(cfo, cfi):
    if cfo is None or cfi is None:
        return None
    return float(cfo) + float(cfi)

def cfo_quality(cfo, pat):
    value=safe_divide(cfo,pat)
    if value is None: return None, "Not Available"
    if value > 1: return value, "High Quality"
    if value >= .5: return value, "Moderate"
    return value, "Accrual Risk"

def capex_intensity(capex, sales):
    value=safe_divide(abs(capex),sales)
    if value is None: return None, "Not Available"
    value*=100
    if value < 3: return value, "Asset Light"
    if value <= 8: return value, "Moderate"
    return value, "Capital Intensive"
