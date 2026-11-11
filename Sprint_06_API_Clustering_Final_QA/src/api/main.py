from fastapi import FastAPI
from src.api.routers import health,companies,screener,sectors,peers,valuation,portfolio,documents
app=FastAPI(title="N100 Financial Intelligence API",version="1.0.0",description="Read-only financial intelligence API backed by the supplied Nifty 100 dataset.")
for r in [health.router,companies.router,screener.router,sectors.router,peers.router,valuation.router,portfolio.router,documents.router]: app.include_router(r)
@app.get("/",tags=["health"])
def root(): return {"name":"N100 Financial Intelligence API","docs":"/docs","openapi":"/openapi.json"}
