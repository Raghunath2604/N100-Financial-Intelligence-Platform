from pathlib import Path
from .loader import run_pipeline

if __name__ == "__main__":
    root=Path(__file__).resolve().parents[2]
    tables,dq,audit,fk,quarantine=run_pipeline(root)
    print(f"Companies in master: {len(tables['companies'])}")
    print(f"Source tables loaded: {len(audit)}")
    print(f"Source rows quarantined: {sum(len(x) for x in quarantine.values())}")
    print(f"Data-quality findings: {len(dq)}")
    print(f"SQLite foreign-key violations: {len(fk)}")
    if fk:
        raise SystemExit("Foreign-key validation failed")
