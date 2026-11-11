
import importlib.util, sys, sqlite3, pandas as pd
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("screener_acceptance",ROOT/"src/screener/engine.py")
mod=importlib.util.module_from_spec(spec);sys.modules["screener_acceptance"]=mod;spec.loader.exec_module(mod)

def test_latest_annual_march_period_preferred():
    d=mod.load_universe(ROOT/"database"/"nifty100.db")
    assert (d.loc[~d.annual_period_fallback,"year"].astype(str).str.endswith("-03")).all()

def test_interim_only_company_is_retained_and_flagged():
    d=mod.load_universe(ROOT/"database"/"nifty100.db")
    assert d.company_id.nunique()==92
    assert d.annual_period_fallback.sum()==1

def test_composite_score_available_for_full_universe():
    d=mod.add_quality_scores(mod.load_universe(ROOT/"database"/"nifty100.db"))
    assert d.composite_quality_score.notna().sum()==92
    assert d.composite_quality_score.between(0,100).all()

def test_peer_percentile_table_is_persisted():
    con=sqlite3.connect(ROOT/"database"/"nifty100.db")
    assert con.execute("select count(*) from peer_percentiles").fetchone()[0]>0
    con.close()

def test_peer_group_workbook_contains_twenty_metrics_plus_percentiles():
    x=pd.read_excel(ROOT/"output"/"peer_comparison.xlsx",sheet_name=0)
    assert len([c for c in x.columns if not c.endswith("_percentile") and c not in ["company_id","company_name"]])>=20

def test_fourteen_dq_rules_pass():
    dq=pd.read_csv(ROOT/"output"/"sprint3_data_quality_checks.csv")
    assert len(dq)==14
    assert (dq.status=="PASS").all()

def test_unassigned_peer_companies_are_explicitly_reported():
    f=pd.read_csv(ROOT/"output"/"companies_without_peer_group.csv")
    assert "peer_group_status" in f.columns
    assert f.peer_group_status.eq("No peer group assigned").all()

def test_turnaround_preset_supported():
    assert "revenue_cagr3_min" in mod.PRESETS["Turnaround Watch"]
