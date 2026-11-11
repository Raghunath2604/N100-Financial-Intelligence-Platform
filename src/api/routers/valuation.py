from fastapi import APIRouter
from src.api.db import rows
router=APIRouter(prefix="/valuation",tags=["valuation"])
@router.get("/market-cap-history/{company_id}")
def market_cap_history(company_id:str): return rows("SELECT * FROM market_cap WHERE company_id=? ORDER BY year",(company_id,))
