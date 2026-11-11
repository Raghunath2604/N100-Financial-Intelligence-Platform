import pytest
from src.etl.normaliser import normalize_ticker

@pytest.mark.parametrize("raw,expected", [
(" tcs ","TCS"),("hdfcbank","HDFCBANK"),("INFY","INFY"),
("abb","ABB"),("  RELIANCE  ","RELIANCE"),("sbi","SBI"),
("TataSteel","TATASTEEL"),("AdaniEnt","ADANIENT"),
("  icicibank","ICICIBANK"),("lt","LT"),("M&M","M&M"),
("BAJAJ-AUTO","BAJAJ-AUTO"),("  SBILIFE  ","SBILIFE"),
("  ",None),(None,None),
])
def test_normalize_ticker(raw,expected):
    assert normalize_ticker(raw)==expected
