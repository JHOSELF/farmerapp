from fastapi import FastAPI
from .routers import disease, advice, market
from .db import create_database_tables

app = FastAPI(
	title="AI Farmer Assistant",
	description="Identify crop diseases from photos, get real-time farming advice, and connect to a simple marketplace.",
	version="0.1.0",
)

@app.on_event("startup")
def on_startup() -> None:
	create_database_tables()

app.include_router(disease.router, prefix="/disease", tags=["Disease Detection"])
app.include_router(advice.router, prefix="/advice", tags=["Farming Advice"])
app.include_router(market.router, prefix="/market", tags=["Marketplace"])

@app.get("/health")
def health() -> dict:
	return {"status": "ok"}