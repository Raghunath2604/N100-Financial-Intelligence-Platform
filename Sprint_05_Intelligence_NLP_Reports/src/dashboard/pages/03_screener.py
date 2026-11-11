
import streamlit as st
import pandas as pd
from src.dashboard.pages.common import universe
def render():
    st.title("Fundamental Screener")
    df=universe()
    st.caption("Filters operate on latest annual financial ratios and the latest dated market snapshot. Missing values are not treated as passes.")
    presets=["All companies","Quality Compounder","Value Pick","Growth Accelerator","Dividend Champion","Debt-Free Blue Chip","Turnaround Watch"]
    preset=st.selectbox("Strategy preset",presets)
    if preset!="All companies":
        from src.screener.engine import PRESETS,apply_filters
        df=apply_filters(df,PRESETS[preset])
    with st.expander("Custom filters",expanded=True):
        a,b,c,d=st.columns(4)
        min_roe=a.slider("Minimum ROE (%)",0.0,50.0,0.0,1.0)
        min_roce=b.slider("Minimum ROCE (%)",0.0,60.0,0.0,1.0)
        max_de=c.slider("Maximum debt/equity",0.0,5.0,5.0,0.1)
        min_fcf=d.slider("Minimum FCF (₹ Cr)",-50000.0,50000.0,-50000.0,500.0)
        a,b,c,d=st.columns(4)
        min_rev_cagr=a.slider("Minimum revenue CAGR 5Y (%)",-50.0,60.0,-50.0,1.0)
        min_pat_cagr=b.slider("Minimum PAT CAGR 5Y (%)",-50.0,100.0,-50.0,1.0)
        max_pe=c.slider("Maximum P/E",1.0,150.0,150.0,1.0)
        max_pb=d.slider("Maximum P/B",0.0,50.0,50.0,0.5)
        a,b=st.columns(2)
        min_div=a.slider("Minimum dividend yield (%)",0.0,15.0,0.0,0.1)
        min_cap=b.slider("Minimum market cap (₹ Cr)",0.0,2000000.0,0.0,1000.0)
    # Filters are conjunctive; finance companies are exempt from generic D/E cutoffs.
    if min_roe>0: df=df[df.return_on_equity_pct.notna() & (df.return_on_equity_pct>=min_roe)]
    if min_roce>0: df=df[df.return_on_capital_pct.notna() & (df.return_on_capital_pct>=min_roce)]
    if max_de<5:
        finance=pd.to_numeric(df.financial_sector_flag,errors="coerce").eq(1)
        df=df[(finance)|(df.debt_to_equity.notna() & (df.debt_to_equity<=max_de))]
    if min_fcf>-50000: df=df[df.free_cash_flow_cr.notna() & (df.free_cash_flow_cr>=min_fcf)]
    if min_rev_cagr>-50: df=df[df.revenue_cagr_5y_pct.notna() & (df.revenue_cagr_5y_pct>=min_rev_cagr)]
    if min_pat_cagr>-50: df=df[df.pat_cagr_5y_pct.notna() & (df.pat_cagr_5y_pct>=min_pat_cagr)]
    if max_pe<150: df=df[df.pe_ratio.notna() & (df.pe_ratio<=max_pe)]
    if max_pb<50: df=df[df.pb_ratio.notna() & (df.pb_ratio<=max_pb)]
    if min_div>0: df=df[df.dividend_yield_pct.notna() & (df.dividend_yield_pct>=min_div)]
    if min_cap>0: df=df[df.market_cap_crore.notna() & (df.market_cap_crore>=min_cap)]
    st.metric("Matching companies",len(df))
    sortcol="composite_quality_score" if "composite_quality_score" in df else "return_on_equity_pct"
    st.dataframe(df.sort_values(sortcol,ascending=False),use_container_width=True,hide_index=True)
    st.download_button("Export current results (CSV)",df.to_csv(index=False).encode(),file_name="n100_screener_results.csv",mime="text/csv")
