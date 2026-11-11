from fastapi import APIRouter
from src.api.db import one
router=APIRouter(tags=["health"])
@router.get("/health")
def health(): return {"status":"ok","database":"connected" if one("SELECT 1 AS ok") else "unavailable"}
