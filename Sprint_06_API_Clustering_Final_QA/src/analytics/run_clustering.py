from pathlib import Path
from src.analytics.clustering import run_clustering
ROOT=Path(__file__).resolve().parents[2]
if __name__=="__main__":
    result=run_clustering(ROOT/"database"/"nifty100.db",ROOT/"output")
    print(f"Clustered {len(result)} companies into {result.cluster_id.nunique()} clusters")
