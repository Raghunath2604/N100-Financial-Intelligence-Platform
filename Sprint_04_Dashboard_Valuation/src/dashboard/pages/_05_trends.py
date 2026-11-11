
import streamlit as st
import plotly.express as px
from src.dashboard import db
from src.dashboard.pages.common import universe
def render():
    st.title("Financial Trends")
    u=universe(); names=dict(zip(u.company_name.fillna(u.company_id),u.company_id))
    company=st.selectbox("Company",list(names)); cid=names[company]
    hist=db.get_company_history(cid)
    options={"Revenue":"revenue_value","Net profit":"pat_value","ROE":"return_on_equity_pct","ROCE":"return_on_capital_pct","Free cash flow":"free_cash_flow_cr","Debt/equity":"debt_to_equity"}
    selected=st.multiselect("Choose up to three metrics",list(options),default=["Revenue","Net profit"],max_selections=3)
    r=hist["ratios"]
    if r.empty: st.info("No financial history available.");return
    for name in selected:
        col=options[name]
        if col in r and r[col].notna().any():
            st.plotly_chart(px.line(r,x="year",y=col,markers=True,title=name),use_container_width=True)
    if "revenue_value" in r:
        r=r.sort_values("year").copy();r["revenue_yoy_pct"]=r.revenue_value.pct_change()*100
        st.subheader("Revenue year-on-year change")
        st.dataframe(r[["year","revenue_value","revenue_yoy_pct"]].tail(10),hide_index=True,use_container_width=True)
