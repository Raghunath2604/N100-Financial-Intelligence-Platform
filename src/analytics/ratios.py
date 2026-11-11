"""Financial KPI engine for Nifty 100 annual financial statements."""
from __future__ import annotations
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd

def safe_divide(numerator, denominator):
    if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
        return None
    return float(numerator) / float(denominator)

def calculate_cagr(start, end, years):
    """CAGR with explicit sign/zero edge flags; returns (value, flag)."""
    if years is None or years <= 0 or pd.isna(start) or pd.isna(end):
        return None, "INSUFFICIENT_DATA"
    start, end = float(start), float(end)
    if start == 0:
        return None, "ZERO_BASE"
    if start < 0 and end > 0:
        return None, "TURNAROUND"
    if start < 0 and end < 0:
        return None, "BOTH_NEGATIVE"
    if start > 0 and end < 0:
        return None, "DECLINE_TO_LOSS"
    if start > 0 and end >= 0:
        if end == 0:
            return -100.0, "DECLINE_TO_ZERO"
        return ((end / start) ** (1.0 / years) - 1.0) * 100.0, "OK"
    return None, "INVALID_SIGN"

def _latest_years(df, key="year"):
    out=df.copy()
    out["_year_num"]=pd.to_numeric(out[key].astype(str).str[:4],errors="coerce")
    return out.sort_values(["company_id","_year_num","id"] if "id" in out else ["company_id","_year_num"])

def capital_allocation_pattern(cfo, cfi, cff):
    """Classify eight sign combinations of CFO, CFI and CFF."""
    signs=tuple(1 if x>0 else (-1 if x<0 else 0) for x in (cfo,cfi,cff))
    labels={
      (1,-1,-1):"Self-Funded Reinvestment & Returns",
      (1,-1,1):"Growth-Funded by External Capital",
      (1,1,-1):"Cash Harvesting & Debt/Dividend Payment",
      (1,1,1):"Cash Accumulation with Financing",
      (-1,-1,1):"Distress / External Funding",
      (-1,1,1):"Operating Stress with Asset Sales & Funding",
      (-1,-1,-1):"Severe Cash Burn",
      (-1,1,-1):"Asset Liquidation During Operating Stress",
    }
    return labels.get(signs, "Mixed / Neutral Cash Flow")

def compute_ratios(pl, bs, cf, sectors=None):
    """Build one annual KPI record per company/year and add 50+ computed metrics."""
    pl=_latest_years(pl).drop_duplicates(["company_id","year"],keep="last")
    bs=_latest_years(bs).drop_duplicates(["company_id","year"],keep="last")
    cf=_latest_years(cf).drop_duplicates(["company_id","year"],keep="last")
    df=pl.merge(bs,on=["company_id","year"],how="outer",suffixes=("_pl","_bs"))
    df=df.merge(cf,on=["company_id","year"],how="outer",suffixes=("","_cf"))
    df=df[df["year"].notna()].copy()
    if sectors is not None and not sectors.empty:
        sector_cols=[c for c in ["company_id","broad_sector","sub_sector"] if c in sectors]
        df=df.merge(sectors[sector_cols].drop_duplicates("company_id"),on="company_id",how="left")
    else:
        df["broad_sector"]="Unknown"
    out=pd.DataFrame()
    out["company_id"]=df.company_id
    out["year"]=df.year
    out["broad_sector"]=df.broad_sector.fillna("Unknown")
    out["source_year"]=df.get("source_year_pl",df.get("source_year"))
    sales=pd.to_numeric(df.sales,errors="coerce")
    op=pd.to_numeric(df.operating_profit,errors="coerce")
    other=pd.to_numeric(df.other_income,errors="coerce").fillna(0)
    interest=pd.to_numeric(df.interest,errors="coerce")
    depreciation=pd.to_numeric(df.depreciation,errors="coerce").fillna(0)
    pat=pd.to_numeric(df.net_profit,errors="coerce")
    equity=pd.to_numeric(df.equity_capital,errors="coerce").fillna(0)+pd.to_numeric(df.reserves,errors="coerce").fillna(0)
    debt=pd.to_numeric(df.borrowings,errors="coerce").fillna(0)
    assets=pd.to_numeric(df.total_assets,errors="coerce")
    cfo=pd.to_numeric(df.operating_activity,errors="coerce")
    cfi=pd.to_numeric(df.investing_activity,errors="coerce")
    cff=pd.to_numeric(df.financing_activity,errors="coerce")
    fcf=cfo+cfi
    ebit=op-depreciation
    def div_series(a,b):
        return [safe_divide(x,y) for x,y in zip(a,b)]
    out["net_profit_margin_pct"]=div_series(pat,sales)*np.nan if False else div_series(pat,sales)
    out["net_profit_margin_pct"]=[x*100 if x is not None else None for x in out["net_profit_margin_pct"]]
    out["operating_profit_margin_pct"]=[x*100 if x is not None else None for x in div_series(op,sales)]
    out["return_on_equity_pct"]=[x*100 if x is not None else None for x in div_series(pat,equity.where(equity>0))]
    capital=equity+debt
    out["return_on_capital_pct"]=[x*100 if x is not None else None for x in div_series(ebit,capital.where(capital>0))]
    out["debt_to_equity"]=[safe_divide(d,e) if e>0 else None for d,e in zip(debt,equity)]
    out["interest_coverage"]=[safe_divide(o+oi,i) for o,oi,i in zip(op,other,interest)]
    out["icr_label"]=["Debt Free" if pd.notna(i) and i==0 else ("Not Available" if pd.isna(v) else "Covered") for i,v in zip(interest,out["interest_coverage"])]
    out["free_cash_flow_cr"]=fcf
    out["asset_turnover"]=div_series(sales,assets)
    out["net_debt_cr"]=debt-pd.to_numeric(df.investments,errors="coerce").fillna(0)
    out["ebit_cr"]=ebit
    out["ebitda_cr"]=op
    out["total_equity_cr"]=equity
    out["total_debt_cr"]=debt
    out["cash_from_operations_cr"]=cfo
    out["cash_from_investing_cr"]=cfi
    out["cash_from_financing_cr"]=cff
    out["capex_cr"]=cfi.abs()
    out["fcf_conversion_pct"]=[x*100 if x is not None else None for x in div_series(fcf,op)]
    out["cfo_to_pat"]=[safe_divide(x,y) for x,y in zip(cfo,pat)]
    out["capex_intensity_pct"]=[x*100 if x is not None else None for x in div_series(cfi.abs(),sales)]
    out["eps"]=pd.to_numeric(df.eps,errors="coerce")
    out["dividend_payout_pct"]=pd.to_numeric(df.dividend_payout,errors="coerce")
    out["book_value_per_share"]=[safe_divide(e,cap/fv) if pd.notna(fv) and fv>0 else None for e,cap,fv in zip(equity,pd.to_numeric(df.equity_capital,errors="coerce"),pd.to_numeric(df.get("face_value",pd.Series([1]*len(df))),errors="coerce"))]
    out["financial_sector_flag"]=out.broad_sector.str.contains("financial",case=False,na=False)
    out["high_leverage_flag"]=[bool(v is not None and v>5 and not fin) for v,fin in zip(out.debt_to_equity,out.financial_sector_flag)]
    out["negative_fcf_flag"]=fcf<0
    out["debt_free_flag"]=(debt==0)
    out["capital_allocation_pattern"]=[capital_allocation_pattern(a,b,c) if pd.notna(a) and pd.notna(b) and pd.notna(c) else "Insufficient Cash Flow Data" for a,b,c in zip(cfo,cfi,cff)]
    out["opm_source_crosscheck_pct"]=pd.to_numeric(df.opm_percentage,errors="coerce")
    out["opm_difference_pct"]=(out.operating_profit_margin_pct-out.opm_source_crosscheck_pct).abs()
    out["opm_crosscheck_flag"]=out.opm_difference_pct>1
    # Year-on-year ratios and CAGR windows.
    out["_year_num"]=pd.to_numeric(out.year.astype(str).str[:4],errors="coerce")
    for metric,series in [("revenue",sales),("pat",pat),("eps",pd.to_numeric(df.eps,errors="coerce"))]:
        out[f"{metric}_value"]=series.values
        out[f"{metric}_yoy_pct"]=np.nan
        for ticker,idxs in out.groupby("company_id").groups.items():
            ids=list(idxs); ids=sorted(ids,key=lambda i:out.loc[i,"_year_num"])
            for prev,cur in zip(ids,ids[1:]):
                a=out.loc[prev,f"{metric}_value"]; b=out.loc[cur,f"{metric}_value"]
                if pd.notna(a) and a!=0 and pd.notna(b):
                    out.loc[cur,f"{metric}_yoy_pct"]=(b/a-1)*100
        for n in (3,5,10):
            vals=[]; flags=[]
            for ticker,grp in out.groupby("company_id",sort=False):
                grp=grp.sort_values("_year_num")
                lookup={int(y):v for y,v in zip(grp._year_num,grp[f"{metric}_value"]) if pd.notna(y) and pd.notna(v)}
                for ix in grp.index:
                    endyear=out.loc[ix,"_year_num"]
                    start=lookup.get(int(endyear-n)) if pd.notna(endyear) else None
                    end=out.loc[ix,f"{metric}_value"]
                    v,flag=calculate_cagr(start,end,n) if start is not None else (None,"INSUFFICIENT_DATA")
                    vals.append((ix,v,flag))
            for ix,v,flag in vals:
                if f"{metric}_cagr_{n}y_pct" not in out: out[f"{metric}_cagr_{n}y_pct"]=np.nan
                if f"{metric}_cagr_{n}y_flag" not in out: out[f"{metric}_cagr_{n}y_flag"]="INSUFFICIENT_DATA"
                out.loc[ix,f"{metric}_cagr_{n}y_pct"]=v
                out.loc[ix,f"{metric}_cagr_{n}y_flag"]=flag
    # Five-year cash flow quality and distress signals.
    out["cfo_quality_5y_avg"]=np.nan
    for ticker,grp in out.groupby("company_id"):
        grp=grp.sort_values("_year_num")
        for ix in grp.index:
            year=out.loc[ix,"_year_num"]
            hist=grp[(grp._year_num<=year)&(grp._year_num>year-5)].tail(5)
            vals=hist.cfo_to_pat.dropna()
            out.loc[ix,"cfo_quality_5y_avg"]=vals.mean() if len(vals) else np.nan
    out["cfo_quality_label"]=pd.cut(out.cfo_quality_5y_avg,[-np.inf,.5,1,np.inf],labels=["Accrual Risk","Moderate","High Quality"],right=False).astype("object")
    out["capex_intensity_label"]=pd.cut(out.capex_intensity_pct,[-np.inf,3,8,np.inf],labels=["Asset Light","Moderate","Capital Intensive"],right=False).astype("object")
    out["cfo_negative_cff_positive_flag"]=(cfo<0)&(cff>0)
    out["deleveraging_flag"]=False
    for ticker,grp in out.groupby("company_id"):
        grp=grp.sort_values("_year_num")
        prev_debt=None
        for ix in grp.index:
            current=out.loc[ix,"total_debt_cr"]
            out.loc[ix,"deleveraging_flag"]=bool(prev_debt is not None and cff.loc[ix]<0 and current<prev_debt)
            prev_debt=current
    out["fcf_negative_3y_flag"]=False
    for ticker,grp in out.groupby("company_id"):
        grp=grp.sort_values("_year_num")
        vals=grp.free_cash_flow_cr.tolist()
        for j,ix in enumerate(grp.index):
            out.loc[ix,"fcf_negative_3y_flag"]=bool(j>=2 and all(pd.notna(x) and x<0 for x in vals[j-2:j+1]))
    # Broad sector-relative ROCE context; banks/NBFCs are excluded from universal D/E risk flag.
    out["roce_method"]="EBIT / (Equity + Debt)"
    out.loc[out.financial_sector_flag,"roce_method"]="Sector-relative Financials percentile"
    out["roce_sector_percentile"]=out.groupby("broad_sector")["return_on_capital_pct"].rank(pct=True)*100
    out["roce_source_company_pct"]=np.nan
    # 50+ computed KPI fields (excluding metadata).
    out=out.drop(columns=["_year_num"])
    return out

def capital_allocation_frame(ratios):
    cols=["company_id","year","cash_from_operations_cr","cash_from_investing_cr","cash_from_financing_cr","capital_allocation_pattern"]
    return ratios[cols].rename(columns={"cash_from_operations_cr":"CFO","cash_from_investing_cr":"CFI","cash_from_financing_cr":"CFF","capital_allocation_pattern":"pattern_label"})

def populate_database(db_path, ratios):
    """Replace financial_ratios with a typed table and enforced company FK."""
    conn=sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("DROP TABLE IF EXISTS financial_ratios")
        definitions=["id INTEGER PRIMARY KEY AUTOINCREMENT","company_id TEXT NOT NULL REFERENCES companies(id)","year TEXT NOT NULL"]
        for col in ratios.columns:
            if col in {"company_id","year"}: continue
            typ="TEXT" if ratios[col].dtype=="object" else "REAL"
            definitions.append(f'"{col}" {typ}')
        conn.execute("CREATE TABLE financial_ratios ("+", ".join(definitions)+")")
        ratios.to_sql("financial_ratios",conn,index=False,if_exists="append")
        conn.execute("CREATE INDEX idx_financial_ratios_company ON financial_ratios(company_id)")
        conn.execute("CREATE INDEX idx_financial_ratios_year ON financial_ratios(year)")
        conn.commit()
        import shutil
        p = Path(db_path)
        if "database" in p.parts:
            alt = p.parents[1] / "data" / p.name
            if alt.parent.exists():
                shutil.copy2(p, alt)
        elif "data" in p.parts:
            alt = p.parents[1] / "database" / p.name
            if alt.parent.exists():
                shutil.copy2(p, alt)
    finally: conn.close()

def run_engine(db_path, output_dir):
    conn=sqlite3.connect(db_path)
    pl=pd.read_sql_query("SELECT * FROM profitandloss",conn)
    bs=pd.read_sql_query("SELECT * FROM balancesheet",conn)
    cf=pd.read_sql_query("SELECT * FROM cashflow",conn)
    sectors=pd.read_sql_query("SELECT * FROM sectors",conn)
    conn.close()
    ratios=compute_ratios(pl,bs,cf,sectors)
    Path(output_dir).mkdir(parents=True,exist_ok=True)
    ratios.to_csv(Path(output_dir)/"financial_ratios_computed.csv",index=False)
    capital_allocation_frame(ratios).to_csv(Path(output_dir)/"capital_allocation.csv",index=False)
    populate_database(db_path,ratios)
    return ratios
