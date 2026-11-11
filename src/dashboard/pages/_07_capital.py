
import streamlit as st
import plotly.express as px
from src.dashboard.pages.common import universe
def render():
    st.title("Capital Allocation Intelligence")
    df=universe()
    if "capital_allocation_pattern" not in df:
        st.info("Capital-allocation classifications are unavailable.");return
    alloc=df.groupby("capital_allocation_pattern",dropna=False).agg(companies=("company_id","nunique"),fcf=("free_cash_flow_cr","median"),roe=("return_on_equity_pct","median")).reset_index()
    fig=px.treemap(alloc,path=["capital_allocation_pattern"],values="companies",color="roe",hover_data=["fcf"])
    st.plotly_chart(fig,use_container_width=True)
    pattern=st.selectbox("Filter by allocation pattern",alloc.capital_allocation_pattern.fillna("Unclassified").tolist())
    st.dataframe(df[df.capital_allocation_pattern.fillna("Unclassified")==pattern][["company_id","company_name","free_cash_flow_cr","return_on_equity_pct","debt_to_equity"]],hide_index=True,use_container_width=True)
