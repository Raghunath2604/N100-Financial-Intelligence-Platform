"""Config-driven equity screener and peer comparison engine."""
from pathlib import Path
import sqlite3, yaml, pandas as pd, numpy as np
import matplotlib.pyplot as plt

FILTERS={
"roe_min":"return_on_equity_pct","de_max":"debt_to_equity","fcf_min":"free_cash_flow_cr",
"revenue_cagr5_min":"revenue_cagr_5y_pct","pat_cagr5_min":"pat_cagr_5y_pct",
"opm_min":"operating_profit_margin_pct","pe_max":"pe_ratio","pb_max":"pb_ratio",
"dividend_yield_min":"dividend_yield_pct","icr_min":"interest_coverage",
"market_cap_min":"market_cap_crore","net_profit_min":"pat_value",
"eps_cagr5_min":"eps_cagr_5y_pct","asset_turnover_min":"asset_turnover","sales_min":"revenue_value"
}
PRESETS={
"Quality Compounder":{"roe_min":15,"de_max":1,"fcf_min":0,"revenue_cagr5_min":10},
"Value Pick":{"pe_max":20,"pb_max":3,"de_max":2,"dividend_yield_min":1},
"Growth Accelerator":{"pat_cagr5_min":20,"revenue_cagr5_min":15,"de_max":2},
"Dividend Champion":{"dividend_yield_min":2,"dividend_payout_max":80,"fcf_min":0},
"Debt-Free Blue Chip":{"de_max":0,"roe_min":12,"sales_min":5000},
"Turnaround Watch":{"revenue_cagr3_min":10,"fcf_min":0,"de_declining":True}
}
def _year_num(s):
    return pd.to_numeric(s.astype(str).str[:4],errors="coerce")
def load_universe(db):
    con=sqlite3.connect(db)
    r_hist=pd.read_sql_query("SELECT * FROM financial_ratios",con)
    mc=pd.read_sql_query("SELECT * FROM market_cap",con)
    co=pd.read_sql_query("SELECT id AS master_company_id,company_name FROM companies",con)
    se=pd.read_sql_query("SELECT company_id,broad_sector,sub_sector FROM sectors",con)
    pg=pd.read_sql_query("SELECT company_id,peer_group_name,is_benchmark FROM peer_groups",con)
    pl=pd.read_sql_query("SELECT company_id,year,dividend_payout FROM profitandloss",con)
    con.close()
    # The raw extracts include interim Sep/Dec observations. Screen on March year-end
    # statements only; selecting the lexicographically/latest row incorrectly picked
    # interim periods with many blank annual KPI fields.
    r_hist["yn"]=_year_num(r_hist.year)
    r_hist["month"]=r_hist.year.astype(str).str[-2:]
    annual=r_hist[r_hist.month=="03"].copy()
    annual_ids=set(annual.company_id)
    # Keep a clearly marked latest available observation for a ticker with no March
    # statement in the source (SIEMENS in this extract), rather than dropping it.
    fallback=r_hist[~r_hist.company_id.isin(annual_ids)].sort_values(["company_id","yn","id"]).groupby("company_id",as_index=False).tail(1)
    latest=pd.concat([annual.sort_values(["company_id","yn","id"]).groupby("company_id",as_index=False).tail(1),fallback],ignore_index=True)
    latest["annual_period_fallback"]=latest.month.ne("03")
    annual=annual.sort_values(["company_id","yn","id"])
    mc["yn"]=_year_num(mc.year)
    mc["month"]=mc.year.astype(str).str[-2:]
    mc_annual=mc[mc.month=="03"].copy()
    if mc_annual.empty: mc_annual=mc.copy()
    mc_annual=mc_annual.sort_values(["company_id","yn","id"]).groupby("company_id",as_index=False).tail(1)
    pl["yn"]=_year_num(pl.year)
    pl["month"]=pl.year.astype(str).str[-2:]
    pl_annual=pl[pl.month=="03"].copy()
    if pl_annual.empty: pl_annual=pl.copy()
    pl_annual=pl_annual.sort_values(["company_id","yn"]).groupby("company_id",as_index=False).tail(1)
    df=latest.merge(mc_annual[["company_id","pe_ratio","pb_ratio","ev_ebitda","dividend_yield_pct","market_cap_crore","enterprise_value_crore"]],on="company_id",how="left")
    df=df.merge(co,left_on="company_id",right_on="master_company_id",how="left").drop(columns=["master_company_id"])
    df=df.merge(se[["company_id","sub_sector"]].drop_duplicates("company_id"),on="company_id",how="left")
    df=df.merge(pg[["company_id","peer_group_name","is_benchmark"]],on="company_id",how="left")
    df=df.merge(pl_annual[["company_id","dividend_payout"]],on="company_id",how="left")
    # Preserve the complete annual history to determine whether leverage is declining.
    prev=annual.sort_values(["company_id","yn"]).groupby("company_id").tail(2).groupby("company_id").debt_to_equity.agg(list)
    df["de_declining"]=[len(prev.get(t,[]))==2 and pd.notna(prev[t][0]) and pd.notna(prev[t][1]) and prev[t][1]<prev[t][0] for t in df.company_id]
    df["latest_year"]=df.year
    # FCF CAGR: calculate only when the year-5 and latest annual FCF are both positive.
    fcf_map={(row.company_id,int(row.yn)):row.free_cash_flow_cr for row in annual[["company_id","yn","free_cash_flow_cr"]].itertuples() if pd.notna(row.yn)}
    vals=[]
    for row in df[["company_id","yn"]].itertuples(index=False):
        a=fcf_map.get((row.company_id,int(row.yn)-5)) if pd.notna(row.yn) else None
        b=fcf_map.get((row.company_id,int(row.yn))) if pd.notna(row.yn) else None
        vals.append(((b/a)**(1/5)-1)*100 if a is not None and b is not None and a>0 and b>0 else (-100.0 if a is not None and b==0 and a>0 else np.nan))
    df["fcf_cagr_5y_pct"]=vals
    return df

def apply_filters(df, filters):
    out=df.copy()
    for key,val in filters.items():
        if key=="de_declining":
            if val: out=out[out.de_declining]
            continue
        if key=="dividend_payout_max":
            out=out[pd.to_numeric(out.dividend_payout,errors="coerce")<=val]; continue
        if key=="revenue_cagr3_min":
            out=out[pd.to_numeric(out.revenue_cagr_3y_pct,errors="coerce")>=val]; continue
        col=FILTERS.get(key)
        if not col or col not in out: raise ValueError(f"Unsupported filter: {key}")
        x=pd.to_numeric(out[col],errors="coerce")
        if key=="de_max" and "financial_sector_flag" in out:
            out=out[(pd.to_numeric(out.financial_sector_flag,errors="coerce").eq(1) | out.financial_sector_flag.astype(str).str.lower().eq("true")) | (x<=val)]
        elif key.endswith("_max"): out=out[x.notna() & (x<=val)]
        else: out=out[x.notna() & (x>=val)]
    return out

def _winsor_scale(series):
    x=pd.to_numeric(series,errors="coerce")
    if x.notna().sum()<2: return pd.Series(50.0,index=x.index)
    lo,hi=x.quantile(.1),x.quantile(.9)
    x=x.clip(lo,hi)
    if hi==lo: return pd.Series(50.0,index=x.index)
    return ((x-lo)/(hi-lo)*100).fillna(50)

def add_quality_scores(df):
    d=df.copy()
    # Component metrics, oriented so higher is better.
    d["score_roe"]=_winsor_scale(d.return_on_equity_pct)
    d["score_roce"]=_winsor_scale(d.return_on_capital_pct)
    d["score_npm"]=_winsor_scale(d.net_profit_margin_pct)
    d["score_fcf_cagr"]=_winsor_scale(d.fcf_cagr_5y_pct)
    d["score_cfo_pat"]=_winsor_scale(d.cfo_quality_5y_avg)
    d["score_fcf_positive"]=np.where(pd.to_numeric(d.free_cash_flow_cr,errors="coerce")>0,100,0)
    d["score_revenue_growth"]=_winsor_scale(d.revenue_cagr_5y_pct)
    d["score_pat_growth"]=_winsor_scale(d.pat_cagr_5y_pct)
    de=pd.to_numeric(d.debt_to_equity,errors="coerce")
    d["score_de"]=_winsor_scale(-de)
    d["score_icr"]=_winsor_scale(d.interest_coverage)
    d["profitability_score"]=.15*d.score_roe+.10*d.score_roce+.10*d.score_npm
    d["cash_quality_score"]=.15*d.score_fcf_cagr+.10*d.score_cfo_pat+.05*d.score_fcf_positive
    d["growth_score"]=.10*d.score_revenue_growth+.10*d.score_pat_growth
    d["leverage_score"]=.10*d.score_de+.05*d.score_icr
    d["composite_quality_score"]=(d.profitability_score+d.cash_quality_score+d.growth_score+d.leverage_score).clip(0,100)
    # Sector-relative rank, 0-100; retain absolute score as well.
    d["sector_relative_score"]=d.groupby("broad_sector").composite_quality_score.rank(pct=True)*100
    return d

def run_screener(db_path,output_dir,config_path):
    cfg=yaml.safe_load(open(config_path,encoding="utf-8"))
    df=add_quality_scores(load_universe(db_path))
    outdir=Path(output_dir); outdir.mkdir(parents=True,exist_ok=True)
    with pd.ExcelWriter(outdir/"screener_output.xlsx",engine="openpyxl") as writer:
        for name,filters in cfg["presets"].items():
            result=apply_filters(df,filters).sort_values("composite_quality_score",ascending=False)
            result.to_excel(writer,sheet_name=name[:31],index=False)
    return df
def build_peer_percentiles(db_path,df):
    metrics={"roe":"return_on_equity_pct","roce":"return_on_capital_pct","npm":"net_profit_margin_pct",
    "de":"debt_to_equity","fcf":"free_cash_flow_cr","pat_cagr5":"pat_cagr_5y_pct",
    "revenue_cagr5":"revenue_cagr_5y_pct","eps_cagr5":"eps_cagr_5y_pct",
    "icr":"interest_coverage","asset_turnover":"asset_turnover"}
    rows=[]
    for group,g in df.dropna(subset=["peer_group_name"]).groupby("peer_group_name"):
        for metric,col in metrics.items():
            vals=pd.to_numeric(g[col],errors="coerce")
            pct=vals.rank(pct=True,method="average")*100
            if metric=="de": pct=100-pct
            for ix,v in pct.items():
                rows.append({"peer_group_name":group,"company_id":g.loc[ix,"company_id"],"metric":metric,"percentile":v})
    out=pd.DataFrame(rows)
    con=sqlite3.connect(db_path)
    con.execute("DROP TABLE IF EXISTS peer_percentiles")
    out.to_sql("peer_percentiles",con,index=False)
    con.execute("CREATE INDEX idx_peer_pct_group ON peer_percentiles(peer_group_name)")
    con.commit(); con.close()
    return out
def peer_workbooks(df,pct,output_dir):
    outdir=Path(output_dir)
    metrics=["return_on_equity_pct","return_on_capital_pct","net_profit_margin_pct","operating_profit_margin_pct",
    "debt_to_equity","interest_coverage","free_cash_flow_cr","pat_cagr_3y_pct","pat_cagr_5y_pct",
    "revenue_cagr_3y_pct","revenue_cagr_5y_pct","eps_cagr_5y_pct","asset_turnover",
    "pe_ratio","pb_ratio","dividend_yield_pct","market_cap_crore","pat_value","revenue_value",
    "composite_quality_score"]
    with pd.ExcelWriter(outdir/"peer_comparison.xlsx",engine="openpyxl") as w:
        for group,g in df.dropna(subset=["peer_group_name"]).groupby("peer_group_name"):
            part=g[["company_id","company_name"]+metrics].copy()
            p=pct[pct.peer_group_name==group].pivot(index="company_id",columns="metric",values="percentile").add_suffix("_percentile")
            part=part.merge(p,left_on="company_id",right_index=True,how="left")
            part.to_excel(w,sheet_name=group[:31],index=False)
def create_radar_charts(df,output_dir):
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    # Eight axes required by the sprint brief; all axes are higher-is-better 0-100 scores.
    axes=["score_roe","score_roce","score_npm","score_de","score_fcf_cagr",
          "score_pat_growth","score_revenue_growth","composite_quality_score"]
    labels=["ROE","ROCE","NPM","D/E (inverse)","FCF score","PAT CAGR5","Revenue CAGR5","Composite"]
    made=0
    for _,r in df.iterrows():
        group=df[df.peer_group_name==r.peer_group_name] if pd.notna(r.peer_group_name) else df
        vals=[float(r[c]) if pd.notna(r[c]) else 50.0 for c in axes]
        avgs=[float(pd.to_numeric(group[c],errors="coerce").mean()) if pd.to_numeric(group[c],errors="coerce").notna().any() else 50.0 for c in axes]
        angles=np.linspace(0,2*np.pi,len(labels),endpoint=False).tolist()
        v=vals+[vals[0]]; a=avgs+[avgs[0]]; angles+=angles[:1]
        fig=plt.figure(figsize=(6,6)); ax=fig.add_subplot(111,polar=True)
        ax.plot(angles,v,label=str(r.company_id)); ax.fill(angles,v,alpha=.15)
        ax.plot(angles,a,"--",label="Peer average" if pd.notna(r.peer_group_name) else "Nifty 100 average")
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels,fontsize=8); ax.set_ylim(0,100)
        group_name=r.peer_group_name if pd.notna(r.peer_group_name) else "Nifty 100 benchmark"
        ax.set_title(f"{r.company_id} — {group_name}",fontsize=10)
        ax.legend(loc="upper right",bbox_to_anchor=(1.3,1.1),fontsize=7)
        fig.tight_layout(); fig.savefig(out/f"{r.company_id}_radar.png",dpi=110); plt.close(fig); made+=1
    return made

def format_workbooks(path,percentile_columns=()):
    from openpyxl import load_workbook
    from openpyxl.styles import PatternFill, Font
    wb=load_workbook(path)
    green=PatternFill("solid",fgColor="C6EFCE")
    yellow=PatternFill("solid",fgColor="FFEB9C")
    red=PatternFill("solid",fgColor="FFC7CE")
    amber=PatternFill("solid",fgColor="F4B183")
    for ws in wb.worksheets:
        ws.freeze_panes="C2"; ws.auto_filter.ref=ws.dimensions
        for cell in ws[1]:
            cell.font=Font(bold=True,color="FFFFFF")
            cell.fill=PatternFill("solid",fgColor="1F4E78")
        headers={c.value:i+1 for i,c in enumerate(ws[1])}
        for col in ws.columns:
            letter=col[0].column_letter
            ws.column_dimensions[letter].width=min(max(max(len(str(c.value or "")) for c in col[:100])+2,12),30)
        if "is_benchmark" in headers:
            ix=headers["is_benchmark"]
            for row in range(2,ws.max_row+1):
                if ws.cell(row,ix).value in (1,1.0,"1",True):
                    for c in ws[row]: c.fill=amber
        for h,ix in headers.items():
            if h.endswith("_percentile"):
                for row in range(2,ws.max_row+1):
                    cell=ws.cell(row,ix)
                    try:
                        v=float(cell.value)
                        cell.fill=green if v>=75 else red if v<=25 else yellow
                    except (TypeError,ValueError): pass
        # Screener KPI threshold cells: colour populated values green and missing values red.
        if "composite_quality_score" in headers:
            ix=headers["composite_quality_score"]
            for row in range(2,ws.max_row+1):
                cell=ws.cell(row,ix)
                if isinstance(cell.value,(int,float)):
                    cell.fill=green if cell.value>=70 else yellow if cell.value>=40 else red
    wb.save(path)
