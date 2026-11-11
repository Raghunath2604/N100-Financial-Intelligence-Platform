from pathlib import Path
import pandas as pd
from src.analytics.clustering import run_clustering,FEATURES
ROOT=Path(__file__).resolve().parents[2]
def test_cluster_all_companies(tmp_path):
 d=run_clustering(ROOT/"database/nifty100.db",tmp_path); assert len(d)==92
def test_exactly_five_clusters(tmp_path):
 d=run_clustering(ROOT/"database/nifty100.db",tmp_path); assert d.cluster_id.nunique()==5
def test_cluster_columns(tmp_path):
 d=run_clustering(ROOT/"database/nifty100.db",tmp_path); assert list(d.columns)==["company_id","cluster_id","cluster_name","distance_from_centroid"]
def test_labels_complete(tmp_path):
 d=run_clustering(ROOT/"database/nifty100.db",tmp_path); assert d.cluster_name.notna().all()
def test_distance_nonnegative(tmp_path):
 d=run_clustering(ROOT/"database/nifty100.db",tmp_path); assert (d.distance_from_centroid>=0).all()
def test_no_duplicate_companies(tmp_path):
 d=run_clustering(ROOT/"database/nifty100.db",tmp_path); assert d.company_id.is_unique
def test_features_count(): assert len(FEATURES)==5
def test_elbow_exists(tmp_path):
 run_clustering(ROOT/"database/nifty100.db",tmp_path); assert (tmp_path/"elbow_plot.png").stat().st_size>1000
def test_heatmap_exists(tmp_path):
 run_clustering(ROOT/"database/nifty100.db",tmp_path); assert (tmp_path/"correlation_heatmap.png").stat().st_size>1000
def test_outlier_report_exists(tmp_path):
 run_clustering(ROOT/"database/nifty100.db",tmp_path); assert (tmp_path/"outlier_report.csv").exists()
