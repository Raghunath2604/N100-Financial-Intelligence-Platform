
import streamlit as st
import plotly.express as px
from src.dashboard.pages.common import universe
def render():
    st.title("Sector Intelligence")
    df=universe()
    sec=df.groupby("broad_sector",dropna=False).agg(companies=("company_id","nunique"),market_cap_crore=("market_cap_crore","sum"),median_roe=("return_on_equity_pct","median"),median_pe=("pe_ratio","median")).reset_index()
    st.plotly_chart(px.scatter(sec,x="market_cap_crore",y="median_roe",size="companies",color="broad_sector",hover_name="broad_sector",title="Sector market cap vs median ROE"),use_container_width=True)
    st.plotly_chart(px.bar(sec.sort_values("median_pe"),x="broad_sector",y="median_pe",title="Sector median P/E"),use_container_width=True)
    st.dataframe(sec,hide_index=True,use_container_width=True)
