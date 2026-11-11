from fastapi import APIRouter
from src.api.db import rows
router=APIRouter(prefix="/portfolio",tags=["portfolio"])
@router.get("/stats")
def portfolio_stats(): return rows("SELECT broad_sector,COUNT(DISTINCT company_id) AS companies,AVG(return_on_equity_pct) AS avg_roe,AVG(debt_to_equity) AS avg_debt_to_equity,AVG(operating_profit_margin_pct) AS avg_opm FROM financial_ratios WHERE year IN (SELECT MAX(year) FROM financial_ratios GROUP BY company_id) GROUP BY broad_sector ORDER BY broad_sector")
