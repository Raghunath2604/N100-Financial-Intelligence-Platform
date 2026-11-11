
"""Cached SQLite accessors for the N100 dashboard."""
from pathlib import Path
import sqlite3
import pandas as pd
try:
    import streamlit as st
    _cache_query = st.cache_data(ttl=300,show_spinner=False)
except ImportError:
    def _cache_query(fn): return fn

def _connect(db_path="database/nifty100.db"):
    p=Path(db_path)
    if not p.exists():
        p=Path(__file__).resolve().parents[2]/"database"/"nifty100.db"
    return sqlite3.connect(str(p))

@_cache_query
def query_df(sql,params=(),db_path="database/nifty100.db"):
    with _connect(db_path) as con:
        return pd.read_sql_query(sql,con,params=params)

def get_companies(db_path="database/nifty100.db"):
    return query_df("SELECT id AS company_id, company_name, about_company, website, nse_profile, bse_profile FROM companies ORDER BY company_name",db_path=db_path)

def get_universe(db_path="database/nifty100.db",year=None):
    year_filter = "WHERE CAST(substr(year,1,4) AS INTEGER)<=?" if year else ""
    sql=f"""
    WITH annual AS (
      SELECT *, ROW_NUMBER() OVER(PARTITION BY company_id ORDER BY
        CASE WHEN substr(year,-2)='03' THEN 1 ELSE 0 END DESC, year DESC, id DESC) rn
      FROM financial_ratios
      {year_filter}
    ), mc AS (
      SELECT *, ROW_NUMBER() OVER(PARTITION BY company_id ORDER BY year DESC,id DESC) rn
      FROM market_cap
      {year_filter}
    )
    SELECT a.*, c.company_name, c.about_company, c.website, c.nse_profile, c.bse_profile,
      s.sub_sector, s.index_weight_pct, s.market_cap_category,
      m.market_cap_crore, m.enterprise_value_crore, m.pe_ratio, m.pb_ratio,
      m.ev_ebitda, m.dividend_yield_pct,
      p.peer_group_name, p.is_benchmark
    FROM annual a
    LEFT JOIN companies c ON c.id=a.company_id
    LEFT JOIN sectors s ON s.company_id=a.company_id
    LEFT JOIN mc m ON m.company_id=a.company_id AND m.rn=1
    LEFT JOIN peer_groups p ON p.company_id=a.company_id
    WHERE a.rn=1
    """
    params=(int(year),int(year)) if year else ()
    df=query_df(sql,params=params,db_path=db_path)
    try:
        import importlib.util, sys
        engine_path=Path(__file__).resolve().parents[1]/"screener"/"engine.py"
        spec=importlib.util.spec_from_file_location("n100_screener_engine",engine_path)
        engine=importlib.util.module_from_spec(spec);sys.modules["n100_screener_engine"]=engine;spec.loader.exec_module(engine)
        scored=engine.add_quality_scores(engine.load_universe(db_path))
        score_cols=["company_id","composite_quality_score","sector_relative_score"]
        df=df.merge(scored[score_cols].drop_duplicates("company_id"),on="company_id",how="left")
    except Exception:
        df["composite_quality_score"]=pd.NA
        df["sector_relative_score"]=pd.NA
    return df

def get_company_history(company_id,db_path="database/nifty100.db"):
    pl=query_df("SELECT year,sales,net_profit,eps,opm_percentage,dividend_payout FROM profitandloss WHERE company_id=? ORDER BY year",(company_id,),db_path)
    fr=query_df("SELECT year,return_on_equity_pct,return_on_capital_pct,net_profit_margin_pct,operating_profit_margin_pct,debt_to_equity,free_cash_flow_cr,cash_from_operations_cr,cfo_to_pat,revenue_value,pat_value FROM financial_ratios WHERE company_id=? ORDER BY year",(company_id,),db_path)
    cf=query_df("SELECT year,operating_activity,investing_activity,financing_activity,net_cash_flow FROM cashflow WHERE company_id=? ORDER BY year",(company_id,),db_path)
    bs=query_df("SELECT year,total_assets,total_liabilities,borrowings,reserves,equity_capital FROM balancesheet WHERE company_id=? ORDER BY year",(company_id,),db_path)
    return {"pnl":pl,"ratios":fr,"cashflow":cf,"balancesheet":bs}

def get_pros_cons(company_id,db_path="database/nifty100.db"):
    return query_df("SELECT pros,cons FROM prosandcons WHERE company_id=?",(company_id,),db_path)

def get_reports(company_id,db_path="database/nifty100.db"):
    return query_df("SELECT year,annual_report FROM documents WHERE company_id=? ORDER BY year DESC",(company_id,),db_path)

def get_peer_group(peer_group,db_path="database/nifty100.db"):
    return query_df("SELECT pp.company_id,c.company_name,pp.metric,pp.percentile FROM peer_percentiles pp LEFT JOIN companies c ON c.id=pp.company_id WHERE pp.peer_group_name=? ORDER BY pp.company_id,pp.metric",(peer_group,),db_path)
