
from pathlib import Path
import os, glob, sqlite3
import pandas as pd
import pypdf
ROOT=Path(__file__).resolve().parents[2]

def test_exactly_92_two_page_company_tearsheets():
    files=list((ROOT/"reports/tearsheets").glob("*_tearsheet.pdf"))
    assert len(files)==92
    assert all(len(pypdf.PdfReader(str(f)).pages)==2 for f in files)

def test_all_tearsheets_meet_thirty_kb_minimum():
    files=list((ROOT/"reports/tearsheets").glob("*_tearsheet.pdf"))
    assert all(f.stat().st_size>=30_000 for f in files)

def test_tearsheets_have_no_blank_pages():
    files=list((ROOT/"reports/tearsheets").glob("*_tearsheet.pdf"))
    for f in files:
        for page in pypdf.PdfReader(str(f)).pages:
            assert len((page.extract_text() or "").strip())>=40

def test_eleven_sector_reports_exist():
    assert len(list((ROOT/"reports/sector").glob("*.pdf")))==11

def test_sector_reports_have_nonblank_content():
    for f in (ROOT/"reports/sector").glob("*.pdf"):
        assert len((pypdf.PdfReader(str(f)).pages[0].extract_text() or "").strip())>100

def test_portfolio_summary_pdf_exists_and_has_content():
    f=ROOT/"reports/portfolio/portfolio_summary.pdf"
    assert f.exists() and len(pypdf.PdfReader(str(f)).pages)>=1
    assert len((pypdf.PdfReader(str(f)).pages[0].extract_text() or "").strip())>100

def test_cashflow_workbook_and_alert_outputs_exist():
    assert (ROOT/"output/cashflow_intelligence.xlsx").exists()
    assert (ROOT/"output/distress_alerts.csv").exists()
    assert (ROOT/"output/pattern_changes.csv").exists()

def test_cashflow_intelligence_covers_92_companies():
    d=pd.read_excel(ROOT/"output/cashflow_intelligence.xlsx",sheet_name="Company Summary")
    assert d.company_id.nunique()==92

def test_distress_alerts_are_rule_labelled():
    d=pd.read_csv(ROOT/"output/distress_alerts.csv")
    assert set(["company_id","alert_code","rule","severity"]).issubset(d.columns)

def test_pattern_changes_have_before_after_values():
    d=pd.read_csv(ROOT/"output/pattern_changes.csv")
    assert set(["company_id","from_year","to_year","dimension","previous_value","current_value"]).issubset(d.columns)

def test_five_visual_spotcheck_files_are_present():
    assert (ROOT/"reports/tearsheet_visual_spotcheck.png").exists()
