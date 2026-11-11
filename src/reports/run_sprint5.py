
"""Run the Sprint 5 NLP, cash-flow intelligence and PDF report pipelines."""
from pathlib import Path
import sys, argparse
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.nlp.parser import parse_analysis
from src.nlp.pros_cons_generator import generate_pros_cons
from src.analytics.cashflow_kpis import build_cashflow_intelligence
from src.reports.tearsheet import generate_tearsheets,generate_sector_reports,generate_portfolio_summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default="database/nifty100.db")
    p.add_argument("--output",default="output")
    p.add_argument("--reports",default="reports")
    a=p.parse_args()
    parsed,failed,div=parse_analysis(a.db,a.output)
    pc=generate_pros_cons(a.db,a.output)
    summary,alerts,changes=build_cashflow_intelligence(a.db,a.output)
    tears=generate_tearsheets(a.db,a.reports)
    sectors=generate_sector_reports(a.db,a.reports)
    portfolio=generate_portfolio_summary(a.db,a.reports)
    print(f"Parsed rows: {len(parsed)}; parse failures logged: {len(failed)}; divergence flags: {int(div.divergence_flag.sum()) if len(div) else 0}")
    print(f"Pros/cons: {len(pc)} records; {summary.company_id.nunique()} companies; alerts: {len(alerts)}; pattern changes: {len(changes)}")
    print(f"PDFs: {len(tears)} company tearsheets; {len(sectors)} sector/cross-sector reports; portfolio: {portfolio}")
if __name__=="__main__": main()
