
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard import db
from src.dashboard.pages.common import universe
def render():
    st.title("Company Profile")
    df=universe(); names=dict(zip(df.company_name.fillna(df.company_id),df.company_id))
    selected=st.selectbox("Search company",list(names))
    cid=names[selected]; row=df[df.company_id==cid].iloc[0]
    st.subheader(selected)
    st.write(row.get("about_company") or "Company description not available in supplied data.")
    c=st.columns(6)
    for col,label,val in zip(c,["Market cap","P/E","P/B","ROE","ROCE","D/E"],
        [row.get("market_cap_crore"),row.get("pe_ratio"),row.get("pb_ratio"),row.get("return_on_equity_pct"),row.get("return_on_capital_pct"),row.get("debt_to_equity")]):
        col.metric(label,"N/A" if pd.isna(val) else f"{val:,.2f}")
    hist=db.get_company_history(cid)
    pnl=hist["pnl"].tail(10)
    if not pnl.empty:
        st.plotly_chart(px.bar(pnl,x="year",y=["sales","net_profit"],barmode="group",title="Revenue and net profit history (₹ Cr)"),use_container_width=True)
    ratios=hist["ratios"]
    if not ratios.empty:
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=ratios.year,y=ratios.return_on_equity_pct,name="ROE"))
        fig.add_trace(go.Scatter(x=ratios.year,y=ratios.return_on_capital_pct,name="ROCE",yaxis="y2"))
        fig.update_layout(title="ROE and ROCE trend",yaxis=dict(title="ROE (%)"),yaxis2=dict(title="ROCE (%)",overlaying="y",side="right"))
        st.plotly_chart(fig,use_container_width=True)
    st.subheader("Pros and cons")
    pc=db.get_pros_cons(cid)
    if pc.empty: st.info("No pros/cons records supplied for this company.")
    else:
        for _,r in pc.iterrows():
            a,b=st.columns(2);a.success(str(r.pros));b.warning(str(r.cons))
