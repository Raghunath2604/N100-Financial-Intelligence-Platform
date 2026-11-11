from pathlib import Path
import sqlite3
from src.etl.loader import load_workbooks, build_database

def test_all_12_workbooks_load():
    root=Path(__file__).resolve().parents[2]
    tables=load_workbooks(root/"data"/"raw")
    assert len(tables)==12
    assert len(tables["companies"])==92

def test_source_row_counts_preserved_in_loader():
    root=Path(__file__).resolve().parents[2]
    tables=load_workbooks(root/"data"/"raw")
    expected={"profitandloss":1276,"balancesheet":1312,"cashflow":1187,
              "analysis":20,"documents":1585,"prosandcons":16,"sectors":92,
              "stock_prices":5520,"market_cap":552,"financial_ratios":1184,"peer_groups":56}
    assert {k:len(tables[k]) for k in expected}==expected

def test_database_foreign_keys_and_quarantine(tmp_path):
    root=Path(__file__).resolve().parents[2]
    tables=load_workbooks(root/"data"/"raw")
    audit,fk,quarantine=build_database(tables,tmp_path/"test.db")
    assert fk==[]
    assert sum(len(x) for x in quarantine.values())>0
    con=sqlite3.connect(tmp_path/"test.db")
    con.execute("PRAGMA foreign_keys=ON")
    assert con.execute("PRAGMA foreign_keys").fetchone()[0]==1
    assert con.execute("SELECT COUNT(*) FROM companies").fetchone()[0]==92
    # An orphan cannot be inserted into a constrained curated table.
    try:
        con.execute("INSERT INTO sectors (id,company_id,broad_sector,sub_sector,index_weight_pct,market_cap_category) VALUES (999999,'NOT_A_COMPANY','x','x',0,'x')")
        con.commit()
        assert False, "foreign-key constraint should reject unknown company"
    except sqlite3.IntegrityError:
        con.rollback()
    con.close()
