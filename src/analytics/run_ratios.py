from pathlib import Path
from .ratios import run_engine
if __name__ == "__main__":
    root=Path(__file__).resolve().parents[2]
    result=run_engine(root/"database"/"nifty100.db",root/"output")
    print(f"Computed KPI rows: {len(result)}")
    print(f"Companies represented: {result.company_id.nunique()}")
    print(f"Computed KPI columns: {len(result.columns)-4}")
