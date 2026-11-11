
"""Transparent relative-valuation metrics for the N100 universe."""
from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

def build_valuation_summary(db_path="database/nifty100.db"):
    with sqlite3.connect(db_path) as con:
        ratios=pd.read_sql_query("""
          SELECT * FROM financial_ratios
          ORDER BY company_id,
            CASE WHEN substr(year,-2)='03' THEN 1 ELSE 0 END DESC, year DESC, id DESC
        """,con)
        market=pd.read_sql_query("SELECT * FROM market_cap ORDER BY year",con)
        companies=pd.read_sql_query("SELECT id AS company_id,company_name FROM companies",con)
        sectors=pd.read_sql_query("SELECT company_id,sub_sector FROM sectors",con)
    # Latest available market snapshot per company; market data is dated and not a live quote.
    market=market.sort_values(["company_id","year","id"]).groupby("company_id",as_index=False).tail(1)
    ratios["annual_period_fallback"]=~ratios.company_id.isin(ratios.loc[ratios.year.astype(str).str.endswith("-03"),"company_id"])
    ratios=ratios.sort_values(["company_id","year","id"]).groupby("company_id",as_index=False).tail(1)
    df=ratios.merge(market[["company_id","year","market_cap_crore","enterprise_value_crore","pe_ratio","pb_ratio","ev_ebitda","dividend_yield_pct"]],on="company_id",how="left",suffixes=("_financial","_market"))
    df=df.merge(companies,on="company_id",how="left").merge(sectors[["company_id","sub_sector"]].drop_duplicates("company_id"),on="company_id",how="left")
    # Sector medians use the supplied peer market snapshot; require at least 3 observations.
    df["sector_median_pe"]=df.groupby("broad_sector").pe_ratio.transform("median")
    df["sector_pe_sample_size"]=df.groupby("broad_sector").pe_ratio.transform("count")
    df["pe_to_sector_median"]=df.pe_ratio/df.sector_median_pe.replace(0,np.nan)
    df["fcf_yield_pct"]=np.where(df.market_cap_crore>0,df.free_cash_flow_cr/df.market_cap_crore*100,np.nan)
    df["valuation_flag"]="In line / insufficient benchmark"
    df.loc[(df.pe_to_sector_median>1.5)&(df.sector_pe_sample_size>=3),"valuation_flag"]="Caution: PE > 1.5x sector median"
    df.loc[(df.pe_to_sector_median<0.7)&(df.pe_ratio>0)&(df.sector_pe_sample_size>=3),"valuation_flag"]="Potential discount: PE < 0.7x sector median"
    df.loc[df.pe_ratio.isna() | df.sector_median_pe.isna() | (df.sector_pe_sample_size<3),"valuation_flag"]="Insufficient valuation data"
    df["market_snapshot_year"]=df.year_market
    df["financial_year"]=df.year_financial
    keep=["company_id","company_name","broad_sector","sub_sector","financial_year","market_snapshot_year","annual_period_fallback",
      "market_cap_crore","enterprise_value_crore","pe_ratio","sector_median_pe","sector_pe_sample_size",
      "pe_to_sector_median","pb_ratio","ev_ebitda","dividend_yield_pct","free_cash_flow_cr",
      "fcf_yield_pct","return_on_equity_pct","return_on_capital_pct","debt_to_equity","valuation_flag"]
    return df[[c for c in keep if c in df.columns]].sort_values("market_cap_crore",ascending=False)

def export_valuation(db_path="database/nifty100.db",output_dir="output"):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    df=build_valuation_summary(db_path)
    df.to_excel(out/"valuation_summary.xlsx",index=False)
    format_valuation_workbook(out/"valuation_summary.xlsx")
    df[["company_id","company_name","broad_sector","pe_ratio","sector_median_pe","pe_to_sector_median","valuation_flag"]].to_csv(out/"valuation_flags.csv",index=False)
    return df


def format_valuation_workbook(path):
    from openpyxl import load_workbook
    from openpyxl.styles import PatternFill, Font
    from openpyxl.formatting.rule import CellIsRule
    wb=load_workbook(path);ws=wb.active
    ws.freeze_panes="C2";ws.auto_filter.ref=ws.dimensions
    for cell in ws[1]:
        cell.font=Font(bold=True,color="FFFFFF")
        cell.fill=PatternFill("solid",fgColor="1F4E78")
    for col in ws.columns:
        letter=col[0].column_letter
        ws.column_dimensions[letter].width=min(max(max(len(str(c.value or "")) for c in col[:100])+2,12),32)
    headers={c.value:i+1 for i,c in enumerate(ws[1])}
    if "pe_to_sector_median" in headers:
        ix=headers["pe_to_sector_median"]
        for row in range(2,ws.max_row+1):
            cell=ws.cell(row,ix)
            try:
                v=float(cell.value)
                if v>1.5: cell.fill=PatternFill("solid",fgColor="FFC7CE")
                elif v<0.7: cell.fill=PatternFill("solid",fgColor="C6EFCE")
                else: cell.fill=PatternFill("solid",fgColor="FFEB9C")
            except (TypeError,ValueError): pass
    wb.save(path)
