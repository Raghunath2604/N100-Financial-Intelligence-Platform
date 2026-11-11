from fastapi import APIRouter
from src.api.db import rows
router=APIRouter(prefix="/peers",tags=["peers"])
@router.get("/{company_id}")
def peers(company_id:str): return rows("SELECT p.peer_group_name,p.company_id,c.company_name,p.is_benchmark FROM peer_groups p LEFT JOIN companies c ON c.id=p.company_id WHERE p.peer_group_name IN (SELECT peer_group_name FROM peer_groups WHERE company_id=?)",(company_id,))
@router.get("/{company_id}/comparison")
def peer_comparison(company_id:str): return rows("SELECT * FROM peer_percentiles WHERE company_id=? ORDER BY metric",(company_id,))
