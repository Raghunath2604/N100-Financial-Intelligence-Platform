import pytest
from src.analytics.ratios import safe_divide, calculate_cagr, capital_allocation_pattern

@pytest.mark.parametrize("a,b,expected",[(10,2,5),(0,5,0),(-10,2,-5),(5,10,.5),(100,4,25)])
def test_safe_divide(a,b,expected): assert safe_divide(a,b)==expected

@pytest.mark.parametrize("a,b",[(1,0),(None,2),(2,None)])
def test_safe_divide_invalid(a,b): assert safe_divide(a,b) is None

@pytest.mark.parametrize("start,end,years,expected,flag",[
(100,121,2,10.0,"OK"),(100,100,5,0.0,"OK"),(100,0,3,-100.0,"DECLINE_TO_ZERO"),
(-10,10,3,None,"TURNAROUND"),(-10,-5,3,None,"BOTH_NEGATIVE"),
(10,-5,3,None,"DECLINE_TO_LOSS"),(0,10,3,None,"ZERO_BASE"),
(10,20,0,None,"INSUFFICIENT_DATA"),(None,20,3,None,"INSUFFICIENT_DATA"),
(100,133.1,3,10.0,"OK")
])
def test_cagr_cases(start,end,years,expected,flag):
    value,actual=calculate_cagr(start,end,years)
    assert actual==flag
    if expected is None: assert value is None
    else: assert value==pytest.approx(expected,abs=1e-7)

@pytest.mark.parametrize("signs,label",[
((1,-1,-1),"Self-Funded Reinvestment & Returns"),
((1,-1,1),"Growth-Funded by External Capital"),
((1,1,-1),"Cash Harvesting & Debt/Dividend Payment"),
((1,1,1),"Cash Accumulation with Financing"),
((-1,-1,1),"Distress / External Funding"),
((-1,1,1),"Operating Stress with Asset Sales & Funding"),
((-1,-1,-1),"Severe Cash Burn"),
((-1,1,-1),"Asset Liquidation During Operating Stress")
])
def test_capital_allocation_patterns(signs,label):
    assert capital_allocation_pattern(*signs)==label
