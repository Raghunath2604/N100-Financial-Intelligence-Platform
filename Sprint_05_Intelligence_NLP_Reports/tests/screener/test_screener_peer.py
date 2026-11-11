import importlib.util, sys, sqlite3, pandas as pd, numpy as np, pytest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("screener_engine_test",ROOT/"src/screener/engine.py")
mod=importlib.util.module_from_spec(spec);sys.modules["screener_engine_test"]=mod;spec.loader.exec_module(mod)

def sample():
    return pd.DataFrame({
      "return_on_equity_pct":[10,20,30],"debt_to_equity":[.5,1.5,0],
      "free_cash_flow_cr":[10,-2,5],"revenue_cagr_5y_pct":[12,18,5],
      "pat_cagr_5y_pct":[15,25,8],"operating_profit_margin_pct":[10,20,15],
      "pe_ratio":[15,25,10],"pb_ratio":[2,4,1],"dividend_yield_pct":[2,0,3],
      "interest_coverage":[4,2,0],"market_cap_crore":[100,200,300],
      "pat_value":[10,20,30],"eps_cagr_5y_pct":[10,20,5],"asset_turnover":[1,2,3],
      "revenue_value":[100,200,300],"financial_sector_flag":[False,False,True],
      "broad_sector":["A","A","B"],"return_on_capital_pct":[12,18,15],
      "net_profit_margin_pct":[5,10,8],"cfo_quality_5y_avg":[1.2,.4,.8],
      "fcf_cagr_5y_pct":[5,10,2],"company_id":["A","B","C"]})

def test_all_15_filter_definitions_exist():
    assert len(mod.FILTERS)==15

@pytest.mark.parametrize("flt,expected",[
({"roe_min":15},2),({"de_max":1},2),({"fcf_min":0},2),
({"revenue_cagr5_min":10},2),({"pat_cagr5_min":20},1),
({"opm_min":15},2),({"pe_max":20},2),({"pb_max":3},2),
({"dividend_yield_min":1},2),({"icr_min":3},1),
({"market_cap_min":200},2),({"net_profit_min":20},2),
({"eps_cagr5_min":10},2),({"asset_turnover_min":2},2),
({"sales_min":200},2)
])
def test_filter_behaviour(flt,expected):
    assert len(mod.apply_filters(sample(),flt))==expected

def test_financial_sector_not_excluded_by_de_filter():
    d=sample()
    got=mod.apply_filters(d,{"de_max":1})
    assert "C" in got.company_id.tolist()

def test_composite_score_is_bounded():
    d=mod.add_quality_scores(sample())
    assert d.composite_quality_score.between(0,100).all()

def test_score_weights_sum_to_one():
    assert abs(.35+.30+.20+.15-1)<1e-9

def test_six_presets_defined():
    assert len(mod.PRESETS)==6

def test_peer_groups_are_eleven():
    d=mod.load_universe(ROOT/"database"/"nifty100.db")
    assert d.peer_group_name.nunique()==11

def test_peer_percentiles_cover_ten_metrics():
    con=sqlite3.connect(ROOT/"database"/"nifty100.db")
    d=mod.load_universe(ROOT/"database"/"nifty100.db")
    p=mod.build_peer_percentiles(ROOT/"database"/"nifty100.db",d)
    assert p.metric.nunique()==10
    con.close()

def test_screener_workbook_has_six_sheets():
    x=pd.ExcelFile(ROOT/"output"/"screener_output.xlsx")
    assert len(x.sheet_names)==6

def test_peer_workbook_has_eleven_sheets():
    x=pd.ExcelFile(ROOT/"output"/"peer_comparison.xlsx")
    assert len(x.sheet_names)==11

def test_radar_chart_count():
    assert len(list((ROOT/"reports"/"radar_charts").glob("*_radar.png")))==92
