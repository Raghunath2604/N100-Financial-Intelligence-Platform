from fastapi import APIRouter
from src.api.db import rows
router=APIRouter(prefix="/sectors",tags=["sectors"])
@router.get("")
def sectors(): return rows("SELECT broad_sector,COUNT(DISTINCT company_id) AS company_count,AVG(index_weight_pct) AS avg_index_weight_pct FROM sectors GROUP BY broad_sector ORDER BY broad_sector")
@router.get("/{sector_name}/companies")
def sector_companies(sector_name:str): return rows("SELECT c.id AS company_id,c.company_name,s.sub_sector,s.index_weight_pct FROM sectors s JOIN companies c ON c.id=s.company_id WHERE s.broad_sector=? ORDER BY c.company_name",(sector_name,))
