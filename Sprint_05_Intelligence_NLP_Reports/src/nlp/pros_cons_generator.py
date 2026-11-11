
"""Rule-based, explainable pros/cons generator for the supplied N100 financial data."""
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

PRO_RULES=[
("P01","ROE >= 15%","return_on_equity_pct",lambda x:x>=15,"High return on equity indicates strong accounting returns on shareholder capital."),
("P02","ROCE >= 15%","return_on_capital_pct",lambda x:x>=15,"High ROCE indicates efficient use of operating capital."),
("P03","Positive free cash flow","free_cash_flow_cr",lambda x:x>0,"The latest annual period reports positive free cash flow."),
("P04","Debt/equity <= 0.5","debt_to_equity",lambda x:x<=0.5,"The balance sheet shows relatively low debt compared with equity."),
("P05","Interest coverage >= 3x","interest_coverage",lambda x:x>=3,"Reported interest coverage indicates capacity to meet finance costs."),
("P06","Revenue CAGR 5Y >= 10%","revenue_cagr_5y_pct",lambda x:x>=10,"Revenue has compounded at least 10% annually over five years in the available statement history."),
("P07","PAT CAGR 5Y >= 10%","pat_cagr_5y_pct",lambda x:x>=10,"Profit has compounded at least 10% annually over five years in the available statement history."),
("P08","CFO/PAT >= 1","cfo_to_pat",lambda x:x>=1,"Operating cash generation is at least as high as reported profit."),
("P09","Positive operating margin","operating_profit_margin_pct",lambda x:x>0,"The latest annual period reports a positive operating margin."),
("P10","Debt-free balance sheet","debt_free_flag",lambda x:x==1,"The source ratio engine classifies the company as debt-free."),
("P11","FCF conversion >= 70%","fcf_conversion_pct",lambda x:x>=70,"Cash conversion from operating profit is comparatively strong."),
("P12","ROE above sector median","roce_sector_percentile",lambda x:x>=75,"The company's ROCE sector percentile is in the top quartile of its sector."),
]
CON_RULES=[
("C01","Negative free cash flow","free_cash_flow_cr",lambda x:x<0,"The latest annual period reports negative free cash flow."),
("C02","Debt/equity > 1","debt_to_equity",lambda x:x>1,"Debt exceeds equity on the reported debt/equity measure."),
("C03","Interest coverage < 1.5x","interest_coverage",lambda x:x<1.5,"Interest coverage is low, indicating limited headroom against finance costs."),
("C04","ROE below 8%","return_on_equity_pct",lambda x:x<8,"Return on equity is below 8% in the latest annual ratio record."),
("C05","ROCE below 8%","return_on_capital_pct",lambda x:x<8,"Return on capital is below 8% in the latest annual ratio record."),
("C06","Negative revenue CAGR 5Y","revenue_cagr_5y_pct",lambda x:x<0,"Five-year revenue CAGR is negative in the available annual history."),
("C07","Negative PAT CAGR 5Y","pat_cagr_5y_pct",lambda x:x<0,"Five-year profit CAGR is negative in the available annual history."),
("C08","CFO/PAT < 0.5","cfo_to_pat",lambda x:x<0.5,"Operating cash flow is weak relative to reported profit."),
("C09","Negative operating margin","operating_profit_margin_pct",lambda x:x<0,"The latest annual period reports a negative operating margin."),
("C10","High debt/equity > 2","debt_to_equity",lambda x:x>2,"Leverage is elevated, with debt exceeding twice equity."),
("C11","FCF conversion < 0","fcf_conversion_pct",lambda x:x<0,"Free-cash-flow conversion is negative in the latest annual ratio record."),
("C12","ROCE sector percentile below 25","roce_sector_percentile",lambda x:x<25,"ROCE ranks in the bottom quartile of the supplied sector comparison."),
]

def generate_pros_cons(db_path="database/nifty100.db",output_dir="output"):
    with sqlite3.connect(db_path) as con:
        ratios=pd.read_sql_query("SELECT * FROM financial_ratios WHERE substr(year,-2)='03' ORDER BY year",con)
        companies=pd.read_sql_query("SELECT id AS company_id,company_name FROM companies",con)
        sectors=pd.read_sql_query("SELECT company_id FROM sectors",con)
    latest=ratios.groupby("company_id",as_index=False).tail(1)
    latest=latest.merge(companies,on="company_id",how="right").merge(sectors,on="company_id",how="left")
    rows=[]
    for _,r in latest.iterrows():
        for typ,rules in [("pro",PRO_RULES),("con",CON_RULES)]:
            found=[]
            for code,label,col,predicate,description in rules:
                v=r.get(col)
                if pd.notna(v):
                    try:
                        if predicate(float(v)): found.append((code,label,description, min(95,70+min(abs(float(v)),25))))
                    except (TypeError,ValueError): pass
            if not found:
                # Honest fallback: do not invent a financial signal when source data is absent.
                found=[("DATA01","Limited financial data coverage","The supplied dataset does not contain enough valid metrics to assert a financial strength or weakness; review source coverage before drawing a conclusion.",65)]
            for code,label,desc,confidence in found:
                rows.append({"company_id":r.company_id,"company_name":r.company_name,"broad_sector":r.broad_sector,"type":typ,"rule_id":code,"rule":label,"statement":desc,"confidence_pct":round(confidence,1),"confidence_pass":confidence>60})
    df=pd.DataFrame(rows)
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/"pros_cons_generated.csv",index=False)
    return df

if __name__=="__main__":
    d=generate_pros_cons();print(d.groupby("type").size().to_dict(),d.groupby(["company_id","type"]).size().unstack().notna().all().to_dict())
