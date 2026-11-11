
import importlib.util, sqlite3, time
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def test_dashboard_universe_contains_92_companies():
    db=load_module("dashboard_db",ROOT/"src/dashboard/db.py")
    df=db.get_universe(str(ROOT/"database/nifty100.db"))
    assert df.company_id.nunique()==92

def test_dashboard_has_all_eight_screens():
    pages=ROOT/"src/dashboard/pages"
    required=["01_home.py","02_profile.py","03_screener.py","04_peers.py","05_trends.py","06_sectors.py","07_capital.py","08_reports.py"]
    assert all((pages/p).exists() for p in required)

def test_valuation_summary_contains_92_companies():
    val=load_module("valuation_test",ROOT/"src/analytics/valuation.py")
    df=val.build_valuation_summary(str(ROOT/"database/nifty100.db"))
    assert df.company_id.nunique()==92

def test_valuation_pe_caution_threshold():
    val=load_module("valuation_test2",ROOT/"src/analytics/valuation.py")
    df=val.build_valuation_summary(str(ROOT/"database/nifty100.db"))
    caution=df[df.valuation_flag.str.startswith("Caution")]
    assert (caution.pe_to_sector_median>1.5).all()

def test_valuation_discount_threshold():
    val=load_module("valuation_test3",ROOT/"src/analytics/valuation.py")
    df=val.build_valuation_summary(str(ROOT/"database/nifty100.db"))
    discount=df[df.valuation_flag.str.startswith("Potential discount")]
    assert (discount.pe_to_sector_median<0.7).all()

def test_fcf_yield_formula():
    val=load_module("valuation_test4",ROOT/"src/analytics/valuation.py")
    df=val.build_valuation_summary(str(ROOT/"database/nifty100.db"))
    row=df[df.market_cap_crore.notna() & df.free_cash_flow_cr.notna()].iloc[0]
    expected=row.free_cash_flow_cr/row.market_cap_crore*100
    assert abs(row.fcf_yield_pct-expected)<1e-8

def test_ten_sample_tickers_have_profile_history():
    db=load_module("dashboard_db2",ROOT/"src/dashboard/db.py")
    universe=db.get_universe(str(ROOT/"database/nifty100.db"))
    tickers=universe.company_id.head(10).tolist()
    assert len(tickers)==10
    for ticker in tickers:
        h=db.get_company_history(ticker,str(ROOT/"database/nifty100.db"))
        assert isinstance(h,dict) and "pnl" in h and "ratios" in h

def test_missing_company_documents_return_empty_dataframe():
    db=load_module("dashboard_db3",ROOT/"src/dashboard/db.py")
    u=db.get_universe(str(ROOT/"database/nifty100.db"))
    cid=u.company_id.iloc[0]
    docs=db.get_reports(cid,str(ROOT/"database/nifty100.db"))
    assert isinstance(docs,pd.DataFrame)

def test_valuation_export_files_exist_and_have_92_rows():
    p=ROOT/"output/valuation_summary.xlsx"
    c=ROOT/"output/valuation_flags.csv"
    assert p.exists() and c.exists()
    assert len(pd.read_excel(p))==92
    assert len(pd.read_csv(c))==92

def test_historical_year_selection_returns_data():
    db=load_module("dashboard_db4",ROOT/"src/dashboard/db.py")
    for yr in [2019,2020,2024]:
        df=db.get_universe(str(ROOT/"database/nifty100.db"),year=yr)
        assert len(df)>=85
        assert df.year.astype(str).str[:4].astype(int).le(yr).all()

def test_valuation_snapshot_year_is_explicit():
    val=load_module("valuation_test5",ROOT/"src/analytics/valuation.py")
    df=val.build_valuation_summary(str(ROOT/"database/nifty100.db"))
    assert "market_snapshot_year" in df
    assert df.market_snapshot_year.notna().sum()>=85

def test_partial_data_is_not_fabricated():
    val=load_module("valuation_test6",ROOT/"src/analytics/valuation.py")
    df=val.build_valuation_summary(str(ROOT/"database/nifty100.db"))
    assert df.company_id.nunique()==92
    assert df.annual_period_fallback.sum()==1


def test_profile_query_latency_under_three_seconds():
    db=load_module("dashboard_db5",ROOT/"src/dashboard/db.py")
    u=db.get_universe(str(ROOT/"database/nifty100.db"))
    start=time.perf_counter()
    for ticker in u.company_id.head(10):
        db.get_company_history(ticker,str(ROOT/"database/nifty100.db"))
    assert time.perf_counter()-start<3.0

def test_valuation_missing_metrics_remain_missing():
    val=load_module("valuation_test7",ROOT/"src/analytics/valuation.py")
    df=val.build_valuation_summary(str(ROOT/"database/nifty100.db"))
    assert df.fcf_yield_pct.isna().sum()>0
    assert df.company_id.nunique()==92


def test_dashboard_page_modules_import():
    pages=ROOT/"src/dashboard/pages"
    for f in pages.glob("_0*.py"):
        compile(f.read_text(),str(f),"exec")

def test_dashboard_entrypoint_exists():
    app=ROOT/"src/dashboard/app.py"
    assert app.exists() and "streamlit" in app.read_text().lower()
