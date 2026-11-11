
"""N100 Financial Intelligence Platform — Streamlit entry point."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import streamlit as st
from src.dashboard.pages import (
    _01_home as home, _02_profile as profile, _03_screener as screener,
    _04_peers as peers, _05_trends as trends, _06_sectors as sectors,
    _07_capital as capital, _08_reports as reports
)
st.set_page_config(page_title="N100 Financial Intelligence",page_icon="📊",layout="wide",initial_sidebar_state="expanded")
st.sidebar.title("N100 Intelligence")
st.sidebar.caption("Financial research workspace · supplied dataset")
pages={
"01 Home":home.render,"02 Company Profile":profile.render,"03 Screener":screener.render,
"04 Peer Comparison":peers.render,"05 Financial Trends":trends.render,
"06 Sector Intelligence":sectors.render,"07 Capital Allocation":capital.render,
"08 Annual Reports":reports.render}
choice=st.sidebar.radio("Navigate",list(pages))
st.sidebar.divider()
st.sidebar.caption("For research and education only. Not investment advice.")
pages[choice]()
