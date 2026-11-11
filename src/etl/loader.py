"""Robust Excel ingestion with PK/FK constraints and explicit quarantine."""
from pathlib import Path
import sqlite3, time
import pandas as pd
from .normaliser import normalize_year, normalize_ticker
from .validator import validate_data

FILES = {
 "companies":("companies.xlsx",1), "profitandloss":("profitandloss.xlsx",1),
 "balancesheet":("balancesheet.xlsx",1), "cashflow":("cashflow.xlsx",1),
 "analysis":("analysis.xlsx",1), "documents":("documents.xlsx",1),
 "prosandcons":("prosandcons.xlsx",1), "sectors":("sectors.xlsx",0),
 "stock_prices":("stock_prices.xlsx",0), "market_cap":("market_cap.xlsx",0),
 "financial_ratios":("financial_ratios.xlsx",0), "peer_groups":("peer_groups.xlsx",0)
}
def load_workbooks(raw_dir):
    tables={}
    for name,(filename,header) in FILES.items():
        path=Path(raw_dir)/filename
        if not path.exists(): raise FileNotFoundError(f"Missing required source file: {path}")
        df=pd.read_excel(path,header=header,engine="openpyxl")
        df=df.loc[:,~df.columns.astype(str).str.startswith("Unnamed")]
        df.columns=[str(c).strip().lower() for c in df.columns]
        if "company_id" in df: df["company_id"]=df.company_id.map(normalize_ticker)
        if name=="companies" and "id" in df: df["id"]=df.id.map(normalize_ticker)
        if "year" in df:
            df["source_year"]=df["year"].astype("string")
            df["year"]=df["year"].map(normalize_year)
        elif "year" in [str(c).lower() for c in df.columns]:
            raise ValueError(f"Year column normalization failed for {name}")
        tables[name]=df
    return tables

def _sql_type(series):
    if pd.api.types.is_integer_dtype(series): return "INTEGER"
    if pd.api.types.is_numeric_dtype(series): return "REAL"
    return "TEXT"

def _create_table(conn,name,df,company_fk=False,primary_key=True):
    cols=[]
    for col in df.columns:
        q='"'+col.replace('"','""')+'"'
        if col=="id" and primary_key:
            typ="TEXT" if name=="companies" else "INTEGER"
            cols.append(f"{q} {typ} PRIMARY KEY")
        else:
            typ=_sql_type(df[col])
            clause=f"{q} {typ}"
            if col=="company_id" and company_fk:
                clause += ' REFERENCES companies(id) ON UPDATE CASCADE ON DELETE RESTRICT'
            cols.append(clause)
    conn.execute(f'CREATE TABLE "{name}" ({", ".join(cols)})')

def build_database(tables,db_path):
    db_path=Path(db_path); db_path.parent.mkdir(parents=True,exist_ok=True)
    if db_path.exists(): db_path.unlink()
    conn=sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON")
    audit=[]; quarantined={}
    try:
        order=["companies"]+[n for n in tables if n!="companies"]
        for name in order:
            df=tables[name].copy()
            start=time.perf_counter()
            if "id" not in df:
                df.insert(0,"id",range(1,len(df)+1))
            # Preserve duplicate business keys; source id is the true primary key.
            if df["id"].isna().any() or df["id"].duplicated().any():
                raise ValueError(f"{name}: source primary key id contains nulls or duplicates")
            if name=="companies":
                _create_table(conn,name,df,False,True)
                df.to_sql(name,conn,index=False,if_exists="append")
                loaded=df
                rejected=pd.DataFrame(columns=df.columns)
            else:
                if "company_id" in df.columns:
                    valid=set(tables["companies"]["id"].astype(str))
                    mask=df.company_id.astype(str).isin(valid)
                    loaded=df[mask].copy()
                    rejected=df[~mask].copy()
                    quarantined[name]=rejected
                else:
                    loaded=df; rejected=pd.DataFrame(columns=df.columns)
                _create_table(conn,name,loaded,("company_id" in loaded.columns),True)
                if len(loaded): loaded.to_sql(name,conn,index=False,if_exists="append")
                if len(rejected): rejected.to_sql(f"{name}_quarantine",conn,index=False,if_exists="replace")
            if "company_id" in loaded:
                conn.execute(f'CREATE INDEX "idx_{name}_company_id" ON "{name}"(company_id)')
            if "year" in loaded:
                conn.execute(f'CREATE INDEX "idx_{name}_year" ON "{name}"(year)')
            audit.append({"table":name,"source_rows":len(df),"loaded_rows":len(loaded),
                          "quarantined_rows":len(rejected),"primary_key":"id",
                          "foreign_key":"companies(id)" if "company_id" in df.columns and name!="companies" else "n/a",
                          "runtime_s":round(time.perf_counter()-start,4)})
        conn.commit()
        fk=list(conn.execute("PRAGMA foreign_key_check"))
        return audit,fk,quarantined
    finally: conn.close()

def run_pipeline(project_root):
    root=Path(project_root)
    tables=load_workbooks(root/"data"/"raw")
    dq=validate_data(tables)
    for name,df in tables.items(): df.to_csv(root/"data"/"processed"/f"{name}.csv",index=False)
    audit,fk,quarantined=build_database(tables,root/"database"/"nifty100.db")
    import shutil
    shutil.copy2(root/"database"/"nifty100.db", root/"data"/"nifty100.db")
    pd.DataFrame(audit).to_csv(root/"output"/"load_audit.csv",index=False)
    dq.to_csv(root/"output"/"validation_failures.csv",index=False)
    pd.DataFrame([{"check":"foreign_key_check","violations":len(fk)}]).to_csv(root/"output"/"foreign_key_check.csv",index=False)
    qrows=[]
    for name,df in quarantined.items():
        for _,r in df.iterrows():
            qrows.append({"source_table":name,"source_id":r.get("id"),"company_id":r.get("company_id"),
                          "reason":"company_id absent from 92-row companies master"})
    pd.DataFrame(qrows,columns=["source_table","source_id","company_id","reason"]).to_csv(root/"output"/"quarantine_manifest.csv",index=False)
    return tables,dq,audit,fk,quarantined
