
import streamlit as st
import plotly.express as px
from src.dashboard import db
def render():
    st.title("Peer Comparison")
    u=db.get_universe()
    groups=sorted(u.peer_group_name.dropna().unique().tolist())
    if not groups: st.warning("Peer-group mapping is unavailable.");return
    group=st.selectbox("Peer group",groups)
    p=db.get_peer_group(group)
    if p.empty: st.info("No peer percentile data found.");return
    wide=p.pivot_table(index=["company_id","company_name"],columns="metric",values="percentile").reset_index()
    st.dataframe(wide,use_container_width=True,hide_index=True)
    metric=st.selectbox("Percentile metric",sorted(p.metric.unique()))
    st.plotly_chart(px.bar(p[p.metric==metric].sort_values("percentile",ascending=False),x="company_name",y="percentile",title=f"{metric}: peer percentile"),use_container_width=True)
