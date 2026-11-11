
"""Parse CAGR statements supplied in analysis.xlsx without rewriting source values."""
import re, sqlite3
from pathlib import Path
import pandas as pd
PATTERN=re.compile(r"(\d+)\s*Years?\s*:?\s*([\d.]+)\s*%",re.I)
FIELDS={"compounded_sales_growth":"revenue","compounded_profit_growth":"profit","stock_price_cagr":"stock_price","roe":"roe"}

def parse_analysis(db_path="database/nifty100.db",output_dir="output"):
    with sqlite3.connect(db_path) as con:
        raw=pd.read_sql_query("SELECT * FROM analysis ORDER BY company_id,id",con)
        ratios=pd.read_sql_query("SELECT company_id,year,revenue_cagr_5y_pct,pat_cagr_5y_pct,return_on_equity_pct FROM financial_ratios",con)
    rows=[]; failures=[]
    for _,r in raw.iterrows():
        for field,metric in FIELDS.items():
            value=str(r.get(field,"") or "")
            m=PATTERN.search(value)
            if m:
                rows.append({"company_id":r.company_id,"source_row_id":int(r.id),"source_field":field,"metric":metric,"period_years":int(m.group(1)),"parsed_pct":float(m.group(2)),"source_text":value})
            elif value.strip():
                failures.append({"company_id":r.company_id,"source_row_id":int(r.id),"source_field":field,"source_text":value,"failure_reason":"No N Years: X% pattern"})
    parsed=pd.DataFrame(rows);failed=pd.DataFrame(failures)
    # Compare parsed 5Y sales/profit CAGR with the closest 5Y calculated statement metric.
    divergence=[]
    if not parsed.empty:
        calc=ratios.sort_values("year").groupby("company_id").tail(1).set_index("company_id")
        for _,r in parsed[(parsed.period_years==5)&parsed.metric.isin(["revenue","profit"])].iterrows():
            col="revenue_cagr_5y_pct" if r.metric=="revenue" else "pat_cagr_5y_pct"
            val=calc.loc[r.company_id,col] if r.company_id in calc.index else None
            diff=abs(float(r.parsed_pct)-float(val)) if pd.notna(val) else None
            divergence.append({"company_id":r.company_id,"metric":r.metric,"period_years":5,"source_pct":r.parsed_pct,"computed_pct":val,"absolute_divergence_pct_points":diff,"divergence_flag":bool(diff is not None and diff>5)})
    div=pd.DataFrame(divergence)
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    parsed.to_csv(out/"analysis_parsed.csv",index=False)
    failed.to_csv(out/"parse_failures.csv",index=False)
    div.to_csv(out/"cagr_divergence.csv",index=False)
    return parsed,failed,div

if __name__=="__main__":
    p,f,d=parse_analysis();print(f"parsed={len(p)} failures={len(f)} divergences={int(d.divergence_flag.sum()) if len(d) else 0}")
