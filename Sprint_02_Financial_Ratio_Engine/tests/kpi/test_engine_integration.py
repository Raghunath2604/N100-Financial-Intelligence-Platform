from pathlib import Path
import sqlite3
import pandas as pd

def test_ratio_table_meets_minimum_row_count():
    root=Path(__file__).resolve().parents[2]
    con=sqlite3.connect(root/"database"/"nifty100.db")
    count=con.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
    con.close()
    assert count>=1100

def test_ratio_table_has_company_foreign_key():
    root=Path(__file__).resolve().parents[2]
    con=sqlite3.connect(root/"database"/"nifty100.db")
    fks=con.execute("PRAGMA foreign_key_list(financial_ratios)").fetchall()
    con.close()
    assert any(row[2]=="companies" and row[3]=="company_id" and row[4]=="id" for row in fks)

def test_computed_export_has_more_than_50_kpis():
    root=Path(__file__).resolve().parents[2]
    df=pd.read_csv(root/"output"/"financial_ratios_computed.csv")
    assert len(df.columns)-4>=50
