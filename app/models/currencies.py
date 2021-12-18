from datetime import datetime, date

from pydantic import BaseModel, Field
from typing import List

class CurrencyRateResponse(BaseModel):
    source_currency: str = Field(default=..., example="USD")
    target_currency: str = Field(default=..., example="PHP")
    rate: float = Field(default=..., example="49.12")
    date: datetime = Field(default=...)


class CurrencySymbol(BaseModel):
    code: str
    description: str


class CurrencySymbolsResponse(BaseModel):
    supported_currencies: List[CurrencySymbol]
