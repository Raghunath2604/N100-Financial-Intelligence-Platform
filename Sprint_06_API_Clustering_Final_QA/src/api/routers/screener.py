from fastapi import APIRouter
from src.api.db import rows
router=APIRouter(prefix="/screener",tags=["screener"])
@router.get("")
def screen(min_roe:float|None=None,max_de:float|None=None,min_opm:float|None=None,limit:int=100):
 q="""SELECT r.company_id,c.company_name,r.year,r.return_on_equity_pct,r.debt_to_equity,r.operating_profit_margin_pct,r.free_cash_flow_cr FROM financial_ratios r JOIN companies c ON c.id=r.company_id WHERE r.year=(SELECT MAX(x.year) FROM financial_ratios x WHERE x.company_id=r.company_id)"""; p=[]
 if min_roe is not None:q+=" AND r.return_on_equity_pct>=?";p.append(min_roe)
 if max_de is not None:q+=" AND r.debt_to_equity<=?";p.append(max_de)
 if min_opm is not None:q+=" AND r.operating_profit_margin_pct>=?";p.append(min_opm)
 q+=" ORDER BY r.return_on_equity_pct DESC LIMIT ?";p.append(min(max(limit,1),500));return rows(q,p)
