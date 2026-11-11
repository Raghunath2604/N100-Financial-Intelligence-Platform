
import streamlit as st
from src.dashboard import db
from src.dashboard.pages.common import universe
def render():
    st.title("Annual Reports & Company Documents")
    u=universe();names=dict(zip(u.company_name.fillna(u.company_id),u.company_id))
    company=st.selectbox("Company",list(names));cid=names[company]
    docs=db.get_reports(cid)
    if docs.empty: st.info("No annual-report URLs were supplied for this company.");return
    for _,r in docs.iterrows():
        url=str(r.annual_report or "")
        if url.startswith("https://") or url.startswith("http://"):
            st.markdown(f"- [{r.year} Annual Report]({url})")
        else:
            st.warning(f"{r.year}: annual-report link unavailable or invalid in source data.")
    st.caption("Links are taken from the supplied documents workbook. Availability and validity of external documents have not been independently verified.")
