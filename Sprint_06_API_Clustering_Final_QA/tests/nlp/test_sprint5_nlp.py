
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]

def test_analysis_parser_outputs_exist():
    assert (ROOT/"output/analysis_parsed.csv").exists()
    assert (ROOT/"output/parse_failures.csv").exists()

def test_parser_captures_year_cagr_patterns():
    d=pd.read_csv(ROOT/"output/analysis_parsed.csv")
    assert len(d)>0 and d.period_years.isin([1,3,5,10]).all()

def test_parse_failures_are_logged_not_silently_dropped():
    d=pd.read_csv(ROOT/"output/parse_failures.csv")
    assert "failure_reason" in d.columns

def test_cagr_divergence_flags_use_five_percentage_point_threshold():
    d=pd.read_csv(ROOT/"output/cagr_divergence.csv")
    valid=d.absolute_divergence_pct_points.dropna()
    assert (d.loc[valid.index,"divergence_flag"]==(valid>5)).all()

def test_exactly_twelve_pro_and_con_rules_are_defined():
    import ast
    src=(ROOT/"src/nlp/pros_cons_generator.py").read_text()
    tree=ast.parse(src)
    vals={n.targets[0].id:len(n.value.elts) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ["PRO_RULES","CON_RULES"]}
    assert vals["PRO_RULES"]==12 and vals["CON_RULES"]==12

def test_each_company_has_at_least_one_pro_and_con():
    d=pd.read_csv(ROOT/"output/pros_cons_generated.csv")
    counts=d.groupby(["company_id","type"]).size().unstack(fill_value=0)
    assert counts.index.nunique()==92
    assert (counts["pro"]>=1).all() and (counts["con"]>=1).all()

def test_all_generated_confidence_scores_exceed_sixty():
    d=pd.read_csv(ROOT/"output/pros_cons_generated.csv")
    assert d.confidence_pct.gt(60).all()
    assert d.confidence_pass.all()

def test_pros_cons_has_no_unknown_company_ids():
    d=pd.read_csv(ROOT/"output/pros_cons_generated.csv")
    assert d.company_id.nunique()==92
