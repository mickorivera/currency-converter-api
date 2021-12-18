from fastapi import APIRouter

from app.endpoints import exchange_rates


router = APIRouter()
router.include_router(exchange_rates.router, tags=["Exchange Rates"])
