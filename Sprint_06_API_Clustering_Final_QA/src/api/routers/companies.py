from fastapi import APIRouter, HTTPException
from src.api.db import rows,one
router=APIRouter(prefix="/companies",tags=["companies"])
@router.get("")
def companies(limit:int=100,offset:int=0): return rows("SELECT id AS company_id,company_name,website,face_value,book_value,roce_percentage,roe_percentage FROM companies ORDER BY company_name LIMIT ? OFFSET ?",(min(max(limit,1),500),max(offset,0)))
@router.get("/{company_id}")
def profile(company_id:str):
 x=one("SELECT c.*,s.broad_sector,s.sub_sector,s.market_cap_category FROM companies c LEFT JOIN sectors s ON s.company_id=c.id WHERE c.id=?",(company_id,))
 if not x: raise HTTPException(404,"Company not found")
 return x
@router.get("/{company_id}/profit-loss")
def pnl(company_id:str): return rows("SELECT * FROM profitandloss WHERE company_id=? ORDER BY year",(company_id,))
@router.get("/{company_id}/balance-sheet")
def balance(company_id:str): return rows("SELECT * FROM balancesheet WHERE company_id=? ORDER BY year",(company_id,))
@router.get("/{company_id}/cash-flow")
def cashflow(company_id:str): return rows("SELECT * FROM cashflow WHERE company_id=? ORDER BY year",(company_id,))
@router.get("/{company_id}/ratios")
def ratios(company_id:str): return rows("SELECT * FROM financial_ratios WHERE company_id=? ORDER BY year",(company_id,))
@router.get("/{company_id}/tearsheet")
def tearsheet(company_id:str): return {"company":profile(company_id),"ratios":ratios(company_id),"pros_cons":rows("SELECT pros,cons FROM prosandcons WHERE company_id=?",(company_id,))}
