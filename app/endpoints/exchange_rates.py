import json
import logging
from datetime import datetime
from urllib import parse as urlparse

import requests
from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional

from app.config import get_app_settings
from app.models.currencies import CurrencyRateResponse


router = APIRouter()
app_settings = get_app_settings()
logging.basicConfig(
    format=app_settings.log_format, level=app_settings.log_level
)
logger = logging.getLogger(__name__)


@router.get(
    path="/exchange-rates",
    response_model=CurrencyRateResponse,
    response_description="Currency exchange rate on a given date",
    status_code=status.HTTP_200_OK,
    description="Returns exchanges rates given source and target currencies.",
)
def get_exchange_rates(
    source_currency: str,
    target_currency: str,
    year: Optional[int] = Query(default=None, ge=1999),
    month: Optional[int] = Query(default=None, ge=1, le=12),
    day: Optional[int] = Query(default=None, ge=1, le=31),
):
    logger.info(
        f"Processing request for exchange rate"
        f"  for {source_currency}/{target_currency}..."
    )
    cur_date = datetime.now().date()
    try:
        target_date = datetime(year, month, day).date()
    except (ValueError, TypeError):
        logger.warn(
            "Target date either not provided or invalid!"
            " Defaulting to current date..."
        )
        target_date = cur_date

    if target_date > cur_date:
        logger.error(f"Provided date({target_date}) > current date!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date: {target_date}!",
        )

    request_params = {
        "places": app_settings.exchange_rate_decimal_places,
        "base": source_currency.upper(),
        "symbols": target_currency.upper()
    }
    logger.info(
        f"Retrieving exchange rate:"
        f" host: {app_settings.exchange_rate_host}"
        f" date: {str(target_date)}"
        f" params: {request_params}"
    )
    response = requests.get(
        url=urlparse.urljoin(app_settings.exchange_rate_host, str(target_date)),
        params=request_params,
    )
    # TODO: create class for exchange rate api
    if response.status_code != status.HTTP_200_OK:
        logger.error(f"Unable to query exchange rate server: {response.text}!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"External exchange rate server error: {response.text}!"
        )

    response_dict = json.loads(response.text)
    rates = response_dict.get("rates")

    if any(
        [
            len(rates) != 1,
            not response_dict.get("success"),
            response_dict.get("base") != source_currency.upper(),
            response_dict.get("date") != str(target_date),
            not rates.get(target_currency.upper()),
        ]
    ):
        logger.error(f"Invalid exchange rate server response: {response_dict}!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid exchange rate server response!",
        )

    logger.info(
        f"Successfully retrieved exchange rate"
        f" for {source_currency}/{target_currency}: {response_dict}"
    )
    return {
        "source_currency": source_currency,
        "target_currency": target_currency,
        "rate": rates.get(target_currency.upper()),
        "date": datetime.strptime(str(target_date), "%Y-%m-%d"),
    }
