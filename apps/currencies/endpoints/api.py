from fastapi import APIRouter

from apps.currencies.endpoints import exchange_rates


router = APIRouter()
router.include_router(exchange_rates.router, tags=["Exchange Rates"])
