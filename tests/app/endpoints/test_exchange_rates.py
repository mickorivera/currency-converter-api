import json
from datetime import datetime

import pytest
import requests
from fastapi import status
from fastapi.testclient import TestClient
from mockito import ANY, contains, mock, patch, when

from app.v1 import app
from app.config import get_app_settings


app_settings = get_app_settings()


class TestGetExchangeRates:
    def setup_class(self):
        self.client = TestClient(app)
        self.version = "v1"

    @pytest.mark.parametrize(
        "test_data, expected_results",
        [
            (  # success test case: date provided
                {"success": True, "base": "USD", "symbol": "PHP", "date": "2020-02-18", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": 200}
            ),
            (  # success test case: date not provided
                {"success": True, "base": "USD", "symbol": "PHP", "date_missing": True, "date": None, "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": 200}
            ),
            (  # invalid date test case: year < 1999
                {"success": True, "base": "USD", "symbol": "PHP", "date": "1998-01-01", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": 422}
            ),
            (  # invalid date test case: month < 1
                {"success": True, "base": "USD", "symbol": "PHP", "date": "1999-00-01", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": 422}
            ),
            (  # invalid date test case: month > 12
                {"success": True, "base": "USD", "symbol": "PHP", "date": "1999-13-01", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": 422}
            ),
            (  # invalid date test case: day < 1
                {"success": True, "base": "USD", "symbol": "PHP", "date": "1999-01-00", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": 422}
            ),
            (  # invalid date test case: day > 31
                {"success": True, "base": "USD", "symbol": "PHP", "date": "1999-13-32", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": 422}
            ),
            (  # invalid date test case: date > curdate
                {"success": True, "base": "USD", "symbol": "PHP", "date": "2022-01-01", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": 400}
            ),
            (  # invalid date test case: non-existent
                {"success": True, "base": "USD", "symbol": "PHP", "date_invalid": True, "date": "2021-02-31", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": 200}
            ),
            (  # external server failed test case
                {"success": True, "base": "USD", "symbol": "PHP", "date": "2020-02-18", "rates": {"PHP":50.06}, "status_code": status.HTTP_404_NOT_FOUND},
                {"status_code": 500}
            ),
            (  # incorrect rate
                {"success": True, "base": "USD", "symbol": "PHP", "date": "2020-02-18", "rates": {"BTC":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": 500}
            ),
            (  # external server success false
                {"success": False, "base": "USD", "symbol": "PHP", "date": "2020-02-18", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": 500}
            ),
        ]
    )
    def test__get(self, test_data, expected_results):
        mock_exchange_rate_response = mock()
        if test_data.get("date_invalid") or test_data.get("date_missing"):
            test_data["date"] = str(datetime.now().date())
        mock_exchange_rate_response.text = json.dumps(test_data)
        mock_exchange_rate_response.status_code = test_data["status_code"]
        when(requests).get(
            url=f"{app_settings.exchange_rate_host}/{test_data['date']}",
            params={
                'places': app_settings.exchange_rate_decimal_places,
                'base': test_data["base"],
                'symbols': test_data["symbol"],
            },
        ).thenReturn(mock_exchange_rate_response)
        year, month, day = test_data["date"].split("-")
        optional_parameters = ""
        if not test_data.get("date_missing"):
            optional_parameters = (f"&year={year}&month={month}&day={day}")
        response = self.client.get(
            f"/{self.version}/exchange-rates"
            f"?source_currency=usd"
            f"&target_currency=php"
            f"{optional_parameters}"
        )
        assert expected_results["status_code"] == response.status_code
