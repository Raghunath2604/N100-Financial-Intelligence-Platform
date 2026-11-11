
"""Generate Sprint 4 valuation exports."""
import argparse, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from src.analytics.valuation import export_valuation
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default="database/nifty100.db")
    p.add_argument("--output",default="output")
    args=p.parse_args()
    df=export_valuation(args.db,args.output)
    print(f"Generated valuation outputs for {df.company_id.nunique()} companies")
    print(df.valuation_flag.value_counts(dropna=False).to_string())
if __name__=="__main__": main()
