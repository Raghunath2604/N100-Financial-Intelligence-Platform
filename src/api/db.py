import os, sqlite3
from pathlib import Path
def get_db_path():
    env_p = os.getenv("N100_DB_PATH")
    if env_p and Path(env_p).exists():
        return Path(env_p)
    base = Path(__file__).resolve().parents[2]
    if (base / "data" / "nifty100.db").exists():
        return base / "data" / "nifty100.db"
    if (base / "database" / "nifty100.db").exists():
        return base / "database" / "nifty100.db"
    return base / "data" / "nifty100.db"

DB_PATH=get_db_path()
def connect():
    con=sqlite3.connect(DB_PATH); con.row_factory=sqlite3.Row; return con
def rows(sql, params=()):
    con=connect()
    try: return [dict(r) for r in con.execute(sql,params).fetchall()]
    finally: con.close()
def one(sql,params=()):
    data=rows(sql,params); return data[0] if data else None
