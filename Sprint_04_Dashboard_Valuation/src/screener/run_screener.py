"""Run the complete Sprint 3 screener and peer-comparison pipeline."""
from pathlib import Path
import argparse, json, pandas as pd
from engine import load_universe, add_quality_scores, PRESETS, apply_filters, build_peer_percentiles, peer_workbooks, create_radar_charts, format_workbooks

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--db",default="database/nifty100.db")
    parser.add_argument("--output",default="output")
    parser.add_argument("--config",default="src/screener/screener_config.yaml")
    parser.add_argument("--radars",default="reports/radar_charts")
    args=parser.parse_args()
    root=Path.cwd()
    d=add_quality_scores(load_universe(root/args.db))
    out=root/args.output;out.mkdir(parents=True,exist_ok=True)
    import yaml
    cfg=yaml.safe_load(open(root/args.config,encoding="utf-8"))
    with pd.ExcelWriter(out/"screener_output.xlsx",engine="openpyxl") as w:
        for name,filters in cfg["presets"].items():
            apply_filters(d,filters).sort_values("composite_quality_score",ascending=False).to_excel(w,sheet_name=name[:31],index=False)
    pct=build_peer_percentiles(root/args.db,d)
    peer_workbooks(d,pct,out)
    format_workbooks(out/"screener_output.xlsx");format_workbooks(out/"peer_comparison.xlsx")
    charts=create_radar_charts(d,root/args.radars)
    d[d.peer_group_name.isna()][["company_id","company_name"]].assign(peer_group_status="No peer group assigned").to_csv(out/"companies_without_peer_group.csv",index=False)
    counts={n:len(apply_filters(d,f)) for n,f in cfg["presets"].items()}
    manifest={"companies":int(d.company_id.nunique()),"peer_groups":int(d.peer_group_name.nunique()),
      "peer_metrics":int(pct.metric.nunique()),"peer_percentile_rows":int(len(pct)),
      "radar_charts":int(charts),"preset_result_counts":counts}
    (out/"sprint3_manifest.json").write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,indent=2))
if __name__=="__main__": main()
