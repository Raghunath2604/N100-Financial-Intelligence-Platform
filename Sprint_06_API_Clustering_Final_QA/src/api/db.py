import os, sqlite3
from pathlib import Path
DB_PATH=Path(os.getenv("N100_DB_PATH", Path(__file__).resolve().parents[2]/"database"/"nifty100.db"))
def connect():
    con=sqlite3.connect(DB_PATH); con.row_factory=sqlite3.Row; return con
def rows(sql, params=()):
    con=connect()
    try: return [dict(r) for r in con.execute(sql,params).fetchall()]
    finally: con.close()
def one(sql,params=()):
    data=rows(sql,params); return data[0] if data else None
