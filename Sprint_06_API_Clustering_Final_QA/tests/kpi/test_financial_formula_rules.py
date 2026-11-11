import pytest
from src.analytics.ratios import safe_divide, calculate_cagr, capital_allocation_pattern
from src.analytics.cashflow_kpis import free_cash_flow, cfo_quality, capex_intensity

@pytest.mark.parametrize("cfo,cfi,expected",[(100,-30,70),(100,20,120),(-50,-20,-70),(0,0,0),(None,2,None)])
def test_fcf_is_cfo_plus_cfi(cfo,cfi,expected):
    assert free_cash_flow(cfo,cfi)==expected

@pytest.mark.parametrize("cfo,pat,label",[
(120,100,"High Quality"),(100,100,"Moderate"),(75,100,"Moderate"),
(40,100,"Accrual Risk"),(-10,100,"Accrual Risk"),(None,100,"Not Available")
])
def test_cfo_quality_thresholds(cfo,pat,label):
    assert cfo_quality(cfo,pat)[1]==label

@pytest.mark.parametrize("capex,sales,label",[
(2,100,"Asset Light"),(3,100,"Moderate"),(8,100,"Moderate"),
(9,100,"Capital Intensive"),(0,100,"Asset Light"),(10,0,"Not Available")
])
def test_capex_intensity_thresholds(capex,sales,label):
    assert capex_intensity(capex,sales)[1]==label

@pytest.mark.parametrize("a,b,years,flag",[
(100,110,1,"OK"),(100,90,1,"OK"),(100,0,5,"DECLINE_TO_ZERO"),
(0,0,5,"ZERO_BASE"),(-10,0,5,"INVALID_SIGN")
])
def test_cagr_sign_edge_cases(a,b,years,flag):
    assert calculate_cagr(a,b,years)[1]==flag

@pytest.mark.parametrize("signs",[
(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1),
(-1,-1,1),(-1,1,1),(-1,-1,-1),(-1,1,-1)
])
def test_all_eight_capital_allocation_sign_patterns_have_labels(signs):
    assert capital_allocation_pattern(*signs) not in ("Mixed / Neutral Cash Flow",None)
