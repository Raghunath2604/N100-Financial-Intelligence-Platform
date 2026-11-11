
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard import db

def universe():
    return db.get_universe()

def company_options(df):
    return dict(zip(df.company_name.fillna(df.company_id),df.company_id))

def metric_tile(st,label,value,delta=None):
    st.metric(label,value,delta)

def latest_years():
    return ["2019","2020","2021","2022","2023","2024"]

def money(v):
    try: return f"₹{float(v):,.0f} Cr"
    except (TypeError,ValueError): return "N/A"

def line_chart(st,df,x,y,title):
    if not df.empty and x in df and y in df:
        fig=px.line(df,x=x,y=y,markers=True,title=title)
        st.plotly_chart(fig,use_container_width=True)
