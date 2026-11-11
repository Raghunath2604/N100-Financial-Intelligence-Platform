"""Reproducible five-archetype company clustering."""
from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FEATURES = ["return_on_equity_pct", "debt_to_equity", "revenue_cagr_5yr", "fcf_cagr_5yr", "operating_profit_margin_pct"]
NAMES = {0:"Balanced Operators",1:"High-Growth Leaders",2:"Capital-Efficient Compounders",3:"Leveraged Challengers",4:"Cash-Flow Resilient Firms"}

def load_features(db_path):
    con=sqlite3.connect(db_path)
    q="""SELECT r.company_id, r.broad_sector, r.return_on_equity_pct,
    r.debt_to_equity, r.revenue_cagr_5y_pct AS revenue_cagr_5yr,
    r.operating_profit_margin_pct, r.free_cash_flow_cr, r.year
    FROM financial_ratios r"""
    df=pd.read_sql_query(q,con); con.close()
    df["year_num"]=pd.to_numeric(df.year.astype(str).str.extract(r'(\d{4})')[0],errors='coerce')
    df=df.sort_values(['company_id','year_num'])
    fcf=[]
    for cid,g in df.groupby('company_id'):
        g=g.dropna(subset=['free_cash_flow_cr','year_num'])
        val=np.nan
        if len(g)>=2:
            first,last=g.iloc[0],g.iloc[-1]; span=last.year_num-first.year_num
            a,b=first.free_cash_flow_cr,last.free_cash_flow_cr
            if span>=3 and pd.notna(a) and pd.notna(b) and a>0 and b>0: val=((b/a)**(1/span)-1)*100
        fcf.append((cid,val))
    fcf=pd.DataFrame(fcf,columns=['company_id','fcf_cagr_5yr'])
    latest=df.groupby('company_id',as_index=False).tail(1).merge(fcf,on='company_id',how='left')
    cols=['company_id','broad_sector']+FEATURES
    return latest[cols].drop_duplicates('company_id')

def run_clustering(db_path, output_dir):
    output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    data=load_features(db_path)
    con=sqlite3.connect(db_path); companies=pd.read_sql_query('SELECT id, company_name FROM companies',con); con.close()
    data=companies.rename(columns={'id':'company_id'}).merge(data,on='company_id',how='left')
    raw=data[FEATURES].copy()
    for c in FEATURES:
        raw[c]=pd.to_numeric(raw[c],errors='coerce')
        med=data.assign(_v=raw[c]).groupby('broad_sector')['_v'].transform('median')
        raw[c]=raw[c].fillna(med).fillna(raw[c].median()).fillna(0)
    scaler=StandardScaler(); X=scaler.fit_transform(raw)
    km=KMeans(n_clusters=5,random_state=42,n_init=20); labels=km.fit_predict(X)
    distances=np.linalg.norm(X-km.cluster_centers_[labels],axis=1)
    # Archetypes are assigned deterministically by centroid profile, then mapped to readable labels.
    profiles=pd.DataFrame(scaler.inverse_transform(km.cluster_centers_),columns=FEATURES)
    order=list(profiles.sort_values(['revenue_cagr_5yr','return_on_equity_pct'],ascending=False).index)
    archetypes={cluster: name for cluster,name in zip(order,["High-Growth Leaders","Capital-Efficient Compounders","Cash-Flow Resilient Firms","Balanced Operators","Leveraged Challengers"])}
    result=pd.DataFrame({'company_id':data.company_id,'cluster_id':labels,'cluster_name':[archetypes[x] for x in labels],'distance_from_centroid':distances})
    result.to_csv(output_dir/'cluster_labels.csv',index=False)
    # elbow chart
    ks=range(2,11); inertias=[]
    for k in ks: inertias.append(KMeans(n_clusters=k,random_state=42,n_init=10).fit(X).inertia_)
    plt.figure(figsize=(8,5)); plt.plot(list(ks),inertias,marker='o'); plt.axvline(5,linestyle='--'); plt.xlabel('Number of clusters (k)'); plt.ylabel('Inertia'); plt.title('K-Means Elbow Analysis'); plt.tight_layout(); plt.savefig(output_dir/'elbow_plot.png',dpi=160); plt.close()
    corr=raw.corr(numeric_only=True)
    plt.figure(figsize=(8,6)); plt.imshow(corr,aspect='auto',vmin=-1,vmax=1); plt.colorbar(); plt.xticks(range(len(FEATURES)),FEATURES,rotation=45,ha='right'); plt.yticks(range(len(FEATURES)),FEATURES); plt.title('Clustering Feature Correlation'); plt.tight_layout(); plt.savefig(output_dir/'correlation_heatmap.png',dpi=160); plt.close()
    # outliers: top decile distance, with all scores retained
    result.sort_values('distance_from_centroid',ascending=False).head(max(1,int(np.ceil(len(result)*.1)))).to_csv(output_dir/'outlier_report.csv',index=False)
    return result
