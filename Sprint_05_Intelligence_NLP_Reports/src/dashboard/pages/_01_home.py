
import streamlit as st
import plotly.express as px
from src.dashboard.pages.common import universe,metric_tile
def render():
    st.title("N100 | Market Intelligence Overview")
    from src.dashboard.db import get_universe
    year=st.selectbox("Financial year",["2024","2023","2022","2021","2020","2019"],index=0)
    df=get_universe(year=int(year))
    st.caption("Financial statement data is sourced from the supplied project dataset. Market multiples reflect the latest dated market-cap snapshot in that dataset, not live prices.")
    cols=st.columns(3)
    metric_tile(cols[0],"Companies",f"{df.company_id.nunique():,}")
    metric_tile(cols[1],"Sectors",f"{df.broad_sector.nunique():,}")
    metric_tile(cols[2],"Peer groups",f"{df.peer_group_name.nunique():,}")
    cols=st.columns(3)
    metric_tile(cols[0],"Median ROE",f"{df.return_on_equity_pct.median():.1f}%" if df.return_on_equity_pct.notna().any() else "N/A")
    metric_tile(cols[1],"Median ROCE",f"{df.return_on_capital_pct.median():.1f}%" if df.return_on_capital_pct.notna().any() else "N/A")
    metric_tile(cols[2],"Median P/E",f"{df.pe_ratio.median():.1f}x" if df.pe_ratio.notna().any() else "N/A")
    a,b=st.columns(2)
    sector=df.groupby("broad_sector",dropna=False).market_cap_crore.sum().reset_index()
    a.plotly_chart(px.pie(sector,names="broad_sector",values="market_cap_crore",hole=.45,title="Market-cap distribution by sector"),use_container_width=True)
    st.caption("Top-five quality ranking uses the current composite score; financial KPI tiles and sector distribution use the selected financial year.")
    top=df.sort_values("composite_quality_score",ascending=False).head(5)
    b.dataframe(top[["company_name","broad_sector","return_on_equity_pct","return_on_capital_pct","composite_quality_score"]],hide_index=True,use_container_width=True)
    st.subheader("Universe quality distribution")
    st.plotly_chart(px.histogram(df,x="composite_quality_score",nbins=15,title="Composite quality score distribution"),use_container_width=True)
