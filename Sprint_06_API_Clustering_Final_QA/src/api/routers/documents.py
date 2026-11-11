from fastapi import APIRouter
from src.api.db import rows
router=APIRouter(prefix="/documents",tags=["documents"])
@router.get("/{company_id}")
def documents(company_id:str): return rows("SELECT company_id,year,annual_report,source_year FROM documents WHERE company_id=? ORDER BY year DESC",(company_id,))
