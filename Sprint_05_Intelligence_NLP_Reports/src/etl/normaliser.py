"""Canonical normalisers for tickers and financial reporting periods."""
import re
import pandas as pd
MONTHS={"JAN":"01","FEB":"02","MAR":"03","APR":"04","MAY":"05","JUN":"06",
        "JUL":"07","AUG":"08","SEP":"09","OCT":"10","NOV":"11","DEC":"12"}
def normalize_ticker(value):
    if pd.isna(value): return None
    value=str(value).strip().upper()
    return value or None
def normalize_year(value):
    """Return YYYY-MM. TTM/quarterly suffixes map to their stated month/year."""
    if pd.isna(value): return None
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        y=int(value)
        return f"{y:04d}-03" if 1900<=y<=2100 else None
    s=str(value).strip()
    if not s: return None
    if s.upper()=="TTM": return None
    # Handles Mar-23, Mar 2023, Mar 2023 15, Mar 2016 9m
    m=re.search(r"(?i)\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[- /]+(\d{4}|\d{2})\b",s)
    if m:
        mo,yr=m.groups(); y=int(yr)
        if y<100: y += 2000 if y<=69 else 1900
        return f"{y:04d}-{MONTHS[mo.upper()]}"
    m=re.fullmatch(r"(\d{4})[-/](\d{1,2})",s)
    if m:
        y,mo=map(int,m.groups())
        return f"{y:04d}-{mo:02d}" if 1<=mo<=12 else None
    m=re.fullmatch(r"(\d{4})",s)
    if m: return f"{int(s):04d}-03"
    try:
        dt=pd.to_datetime(s,errors="raise")
        return f"{dt.year:04d}-{dt.month:02d}"
    except Exception: return None
