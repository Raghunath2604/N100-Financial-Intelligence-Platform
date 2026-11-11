"""Sixteen deterministic data-quality checks for the Nifty 100 source workbooks."""
import pandas as pd
from .normaliser import normalize_year, normalize_ticker

def validate_data(tables):
    issues=[]
    def add(rule,table,row,field,value,severity,message):
        issues.append(dict(rule_id=rule,table_name=table,row_number=row,company_id=None,
                           field=field,value=str(value),severity=severity,issue=message))
    companies=tables.get("companies",pd.DataFrame())
    known=set(companies["id"].dropna().astype(str)) if "id" in companies else set()
    # DQ-01/02: primary-key completeness and uniqueness.
    for name,df in tables.items():
        if "id" in df:
            for i,v in df["id"].items():
                if pd.isna(v): add("DQ-01",name,i+1,"id",v,"CRITICAL","Primary key is null")
            dup=df[df["id"].duplicated(keep=False)]
            for i,r in dup.iterrows(): add("DQ-02",name,i+1,"id",r["id"],"CRITICAL","Duplicate primary key")
    # DQ-03: company references not present in 92-row master (quarantined at load).
    for name,df in tables.items():
        if name!="companies" and "company_id" in df:
            bad=df[~df.company_id.astype(str).isin(known)]
            for i,r in bad.iterrows(): add("DQ-03",name,i+1,"company_id",r.company_id,"WARNING","Company reference absent from master; row preserved in quarantine table")
    # DQ-04: balance sheet identity check.
    bs=tables.get("balancesheet",pd.DataFrame())
    if {"total_assets","total_liabilities"}.issubset(bs.columns):
        for i,r in bs.iterrows():
            a=pd.to_numeric(r.total_assets,errors="coerce"); l=pd.to_numeric(r.total_liabilities,errors="coerce")
            if pd.notna(a) and pd.notna(l) and abs(a-l)>max(abs(a)*.01,1):
                add("DQ-04","balancesheet",i+1,"total_assets/total_liabilities",f"{a}/{l}","WARNING","Assets and liabilities differ by more than 1%")
    # DQ-05: source OPM cross-check.
    pl=tables.get("profitandloss",pd.DataFrame())
    if {"opm_percentage","operating_profit","sales"}.issubset(pl.columns):
        for i,r in pl.iterrows():
            sales=pd.to_numeric(r.sales,errors="coerce"); op=pd.to_numeric(r.operating_profit,errors="coerce"); margin=pd.to_numeric(r.opm_percentage,errors="coerce")
            if pd.notna(sales) and sales!=0 and pd.notna(op) and pd.notna(margin) and abs(op/sales*100-margin)>1:
                add("DQ-05","profitandloss",i+1,"opm_percentage",margin,"WARNING","Source OPM differs from calculated OPM by more than 1 percentage point")
    # DQ-06: non-positive sales.
    if "sales" in pl:
        for i,r in pl[pd.to_numeric(pl.sales,errors="coerce")<=0].iterrows():
            add("DQ-06","profitandloss",i+1,"sales",r.sales,"WARNING","Sales are zero or negative")
    # DQ-07/08: reporting period and ticker validity.
    for name,df in tables.items():
        if "year" in df:
            for i,v in df.year.items():
                if normalize_year(v) is None:
                    severity="INFO" if str(v).strip().upper()=="TTM" else "WARNING"
                    add("DQ-07",name,i+1,"year",v,severity,"Period is non-annual or unrecognised; original retained in source_year")
        if "company_id" in df:
            for i,v in df.company_id.items():
                t=normalize_ticker(v)
                if not t or not 1<=len(t)<=20:
                    add("DQ-08",name,i+1,"company_id",v,"CRITICAL","Ticker is blank or outside 1-20 characters")
    # DQ-09: cash flow arithmetic.
    cf=tables.get("cashflow",pd.DataFrame())
    if {"net_cash_flow","operating_activity","investing_activity","financing_activity"}.issubset(cf.columns):
        for i,r in cf.iterrows():
            vals=[pd.to_numeric(r[c],errors="coerce") for c in ["net_cash_flow","operating_activity","investing_activity","financing_activity"]]
            if all(pd.notna(v) for v in vals) and abs(vals[0]-sum(vals[1:]))>10:
                add("DQ-09","cashflow",i+1,"net_cash_flow",vals[0],"WARNING","Net cash flow differs from CFO+CFI+CFF by more than 10")
    # DQ-10: negative fixed assets.
    if "fixed_assets" in bs:
        for i,r in bs[pd.to_numeric(bs.fixed_assets,errors="coerce")<0].iterrows():
            add("DQ-10","balancesheet",i+1,"fixed_assets",r.fixed_assets,"WARNING","Fixed assets are negative")
    # DQ-11: unusual tax percentage.
    if "tax_percentage" in pl:
        for i,r in pl[~pd.to_numeric(pl.tax_percentage,errors="coerce").between(0,60)].iterrows():
            add("DQ-11","profitandloss",i+1,"tax_percentage",r.tax_percentage,"WARNING","Tax percentage outside 0-60")
    # DQ-12: unusually high dividend payout.
    if "dividend_payout" in pl:
        for i,r in pl[pd.to_numeric(pl.dividend_payout,errors="coerce")>200].iterrows():
            add("DQ-12","profitandloss",i+1,"dividend_payout",r.dividend_payout,"WARNING","Dividend payout exceeds 200%")
    # DQ-13: missing annual report URLs.
    docs=tables.get("documents",pd.DataFrame())
    if "annual_report" in docs:
        missing=docs[docs.annual_report.isna() | (docs.annual_report.astype(str).str.strip()=="")]
        for i,r in missing.iterrows(): add("DQ-13","documents",i+1,"annual_report",r.annual_report,"WARNING","Annual report URL is missing")
    # DQ-14: EPS sign anomaly.
    if {"eps","net_profit"}.issubset(pl.columns):
        for i,r in pl.iterrows():
            eps=pd.to_numeric(r.eps,errors="coerce"); profit=pd.to_numeric(r.net_profit,errors="coerce")
            if pd.notna(eps) and pd.notna(profit) and profit>0 and eps<=0:
                add("DQ-14","profitandloss",i+1,"eps",eps,"WARNING","EPS is non-positive while net profit is positive")
    # DQ-15: source records with repeated company/year are informational; never discarded.
    for name,df in tables.items():
        if {"company_id","year"}.issubset(df.columns):
            dup=df[df.duplicated(["company_id","year"],keep=False) & df.year.notna()]
            for i,r in dup.iterrows(): add("DQ-15",name,i+1,"company_id/year",f'{r.company_id}/{r.year}',"INFO","Multiple source observations share company and period; preserved by source primary key")
    # DQ-16: short financial history per company across P&L/BS/CF.
    coverage={}
    for name in ["profitandloss","balancesheet","cashflow"]:
        df=tables.get(name,pd.DataFrame())
        if {"company_id","year"}.issubset(df.columns):
            coverage[name]=df.dropna(subset=["year"]).groupby("company_id").year.nunique()
    for ticker in sorted(known):
        counts=[int(coverage.get(n,pd.Series(dtype=int)).get(ticker,0)) for n in ["profitandloss","balancesheet","cashflow"]]
        if min(counts)<5:
            add("DQ-16","coverage",None,"company_id",ticker,"WARNING",f"Financial history under 5 years; P&L/BS/CF={counts}")
    return pd.DataFrame(issues,columns=["rule_id","table_name","row_number","company_id","field","value","severity","issue"])
