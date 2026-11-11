"""Cash-flow KPI and capital-allocation helpers."""
from .ratios import capital_allocation_pattern, safe_divide

def free_cash_flow(cfo, cfi):
    if cfo is None or cfi is None:
        return None
    return float(cfo) + float(cfi)

def cfo_quality(cfo, pat):
    value=safe_divide(cfo,pat)
    if value is None: return None, "Not Available"
    if value > 1: return value, "High Quality"
    if value >= .5: return value, "Moderate"
    return value, "Accrual Risk"

def capex_intensity(capex, sales):
    value=safe_divide(abs(capex),sales)
    if value is None: return None, "Not Available"
    value*=100
    if value < 3: return value, "Asset Light"
    if value <= 8: return value, "Moderate"
    return value, "Capital Intensive"


# ---- Sprint 5 cash-flow intelligence extension ----

"""Cash-flow quality, capital expenditure, distress and pattern-change intelligence."""
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

def build_cashflow_intelligence(db_path="database/nifty100.db",output_dir="output"):
    with sqlite3.connect(db_path) as con:
        ratios=pd.read_sql_query("SELECT * FROM financial_ratios ORDER BY company_id,year,id",con)
        cf=pd.read_sql_query("SELECT * FROM cashflow ORDER BY company_id,year,id",con)
        companies=pd.read_sql_query("SELECT id AS company_id,company_name FROM companies",con)
        sectors=pd.read_sql_query("SELECT company_id,sub_sector FROM sectors",con)
    annual=ratios[ratios.year.astype(str).str.endswith("-03")].copy()
    annual_ids=set(annual.company_id)
    fallback=ratios[~ratios.company_id.isin(annual_ids)].groupby("company_id",as_index=False).tail(1)
    latest=pd.concat([annual.groupby("company_id",as_index=False).tail(1),fallback],ignore_index=True)
    latest=latest.merge(companies,on="company_id",how="right").merge(sectors,on="company_id",how="left")
    # Multi-year cash-flow quality history
    hist=annual.groupby("company_id").agg(
        periods=("year","count"),
        median_cfo_to_pat=("cfo_to_pat","median"),
        negative_fcf_years=("negative_fcf_flag","sum"),
        median_fcf=("free_cash_flow_cr","median"),
        median_capex_intensity=("capex_intensity_pct","median"),
        cfo_negative_cff_positive_years=("cfo_negative_cff_positive_flag","sum")
    ).reset_index()
    out=latest.merge(hist,on="company_id",how="left")
    out["cashflow_quality_assessment"]="Insufficient data"
    out.loc[out.median_cfo_to_pat>=1,"cashflow_quality_assessment"]="Strong cash conversion"
    out.loc[(out.median_cfo_to_pat>=0.5)&(out.median_cfo_to_pat<1),"cashflow_quality_assessment"]="Moderate cash conversion"
    out.loc[out.median_cfo_to_pat<0.5,"cashflow_quality_assessment"]="Weak cash conversion"
    out["capex_intensity_assessment"]="Insufficient data"
    out.loc[out.median_capex_intensity<3,"capex_intensity_assessment"]="Low capex intensity"
    out.loc[out.median_capex_intensity.between(3,10,inclusive="left"),"capex_intensity_assessment"]="Moderate capex intensity"
    out.loc[out.median_capex_intensity>=10,"capex_intensity_assessment"]="High capex intensity"
    out["fcf_stress_flag"]=out.negative_fcf_years.fillna(0)>=3
    out["cash_conversion_risk_flag"]=out.median_cfo_to_pat.notna()&(out.median_cfo_to_pat<0.5)
    out["deleveraging_flag"]=out.deleveraging_flag.fillna(0).eq(1) if "deleveraging_flag" in out else False
    # Distress alert rules are explainable indicators, not credit ratings.
    alerts=[]
    for _,r in out.iterrows():
        rules=[]
        if pd.notna(r.get("debt_to_equity")) and r.debt_to_equity>2: rules.append(("HIGH_LEVERAGE","Debt/equity > 2","High reported leverage"))
        if pd.notna(r.get("interest_coverage")) and r.interest_coverage<1.5 and not bool(r.get("debt_free_flag",0)): rules.append(("LOW_ICR","Interest coverage < 1.5x","Limited reported interest coverage"))
        if bool(r.fcf_stress_flag): rules.append(("REPEATED_NEGATIVE_FCF","Negative FCF in at least 3 annual periods","Repeated free-cash-flow pressure"))
        if bool(r.cash_conversion_risk_flag): rules.append(("WEAK_CASH_CONVERSION","Median CFO/PAT < 0.5","Weak operating cash conversion relative to profit"))
        if pd.notna(r.get("return_on_capital_pct")) and r.return_on_capital_pct<0: rules.append(("NEGATIVE_ROCE","ROCE < 0%","Negative return on capital"))
        for code,rule,desc in rules:
            alerts.append({"company_id":r.company_id,"company_name":r.company_name,"broad_sector":r.broad_sector,"alert_code":code,"rule":rule,"alert":desc,"severity":"High" if code in ["HIGH_LEVERAGE","NEGATIVE_ROCE"] else "Medium"})
    alerts_df=pd.DataFrame(alerts,columns=["company_id","company_name","broad_sector","alert_code","rule","alert","severity"])
    # Detect changes between the latest two annual financial-ratio periods.
    changes=[]
    for cid,g in annual.groupby("company_id"):
        g=g.sort_values("year")
        if len(g)<2: continue
        a,b=g.iloc[-2],g.iloc[-1]
        for col,label in [("capital_allocation_pattern","Capital allocation pattern"),("cfo_quality_label","Cash-flow quality"),("capex_intensity_label","CapEx intensity")]:
            old,new=a.get(col),b.get(col)
            if pd.notna(old) and pd.notna(new) and str(old)!=str(new):
                changes.append({"company_id":cid,"from_year":a.year,"to_year":b.year,"dimension":label,"previous_value":old,"current_value":new})
        if pd.notna(a.debt_to_equity) and pd.notna(b.debt_to_equity) and a.debt_to_equity!=b.debt_to_equity:
            changes.append({"company_id":cid,"from_year":a.year,"to_year":b.year,"dimension":"Debt/equity","previous_value":a.debt_to_equity,"current_value":b.debt_to_equity})
    changes_df=pd.DataFrame(changes,columns=["company_id","from_year","to_year","dimension","previous_value","current_value"])
    # Keep the annual source cashflow rows accessible in the workbook.
    outdir=Path(output_dir);outdir.mkdir(parents=True,exist_ok=True)
    with pd.ExcelWriter(outdir/"cashflow_intelligence.xlsx",engine="openpyxl") as w:
        out.to_excel(w,sheet_name="Company Summary",index=False)
        hist.to_excel(w,sheet_name="Historical Quality",index=False)
        cf.to_excel(w,sheet_name="Cash Flow History",index=False)
        alerts_df.to_excel(w,sheet_name="Distress Alerts",index=False)
        changes_df.to_excel(w,sheet_name="Pattern Changes",index=False)
    alerts_df.to_csv(outdir/"distress_alerts.csv",index=False)
    changes_df.to_csv(outdir/"pattern_changes.csv",index=False)
    return out,alerts_df,changes_df
if __name__=="__main__":
    s,a,c=build_cashflow_intelligence();print("companies",s.company_id.nunique(),"alerts",len(a),"changes",len(c))
