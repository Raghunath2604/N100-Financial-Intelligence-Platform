import pytest
from src.etl.normaliser import normalize_year

@pytest.mark.parametrize("raw,expected", [
("Mar-23","2023-03"),("Dec-12","2012-12"),("Mar 2014","2014-03"),
("Dec 2019","2019-12"),("2024","2024-03"),(2022,"2022-03"),
(2022.0,"2022-03"),("2020-01","2020-01"),("2020/01","2020-01"),
("2020-01-31","2020-01"),("Jan-20","2020-01"),("Feb-21","2021-02"),
("Apr-22","2022-04"),("May-23","2023-05"),("Jun-24","2024-06"),
("Jul-19","2019-07"),("Aug-18","2018-08"),("Sep-17","2017-09"),
("Oct-16","2016-10"),("Nov-15","2015-11"),
])
def test_normalize_year_variants(raw,expected):
    assert normalize_year(raw)==expected

@pytest.mark.parametrize("raw", ["",None,"unknown","FY2022","2022-15","abc-23"])
def test_normalize_year_invalid(raw):
    assert normalize_year(raw) is None
