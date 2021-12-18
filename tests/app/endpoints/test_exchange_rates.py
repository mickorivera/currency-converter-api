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
                {"status_code": status.HTTP_200_OK}
            ),
            (  # success test case: date not provided
                {"success": True, "base": "USD", "symbol": "PHP", "date_missing": True, "date": None, "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": status.HTTP_200_OK}
            ),
            (  # isuccess test case: non-existent date
                {"success": True, "base": "USD", "symbol": "PHP", "date_invalid": True, "date": "2021-02-31", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": status.HTTP_200_OK}
            ),
            (  # invalid date test case: year < 1999
                {"success": True, "base": "USD", "symbol": "PHP", "date": "1998-01-01", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY}
            ),
            (  # invalid date test case: month < 1
                {"success": True, "base": "USD", "symbol": "PHP", "date": "1999-00-01", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY}
            ),
            (  # invalid date test case: month > 12
                {"success": True, "base": "USD", "symbol": "PHP", "date": "1999-13-01", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY}
            ),
            (  # invalid date test case: day < 1
                {"success": True, "base": "USD", "symbol": "PHP", "date": "1999-01-00", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY}
            ),
            (  # invalid date test case: day > 31
                {"success": True, "base": "USD", "symbol": "PHP", "date": "1999-13-32", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY}
            ),
            (  # invalid date test case: date > curdate
                {"success": True, "base": "USD", "symbol": "PHP", "date": "2022-01-01", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": status.HTTP_400_BAD_REQUEST}
            ),
            (  # external server failed test case
                {"success": True, "base": "USD", "symbol": "PHP", "date": "2020-02-18", "rates": {"PHP":50.06}, "status_code": status.HTTP_404_NOT_FOUND},
                {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR}
            ),
            (  # incorrect rate
                {"success": True, "base": "USD", "symbol": "PHP", "date": "2020-02-18", "rates": {"BTC":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR}
            ),
            (  # external server success false
                {"success": False, "base": "USD", "symbol": "PHP", "date": "2020-02-18", "rates": {"PHP":50.06}, "status_code": status.HTTP_200_OK},
                {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR}
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


class TestGetSupportedCurrencies:
    def setup_class(self):
        self.client = TestClient(app)
        self.version = "v1"

    @pytest.mark.parametrize(
        "test_data, expected_results",
        [
            (  # success test case:
                {
                    "ext_api_status_code": status.HTTP_200_OK,
                    "ext_api_body": {
                        "success": True,
                        "symbols": {
                            "PHP": {"code": "PHP", "description": "Philippine Peso"},
                            "USD": {"code": "USD", "description": "US Dollar"},
                        },
                    },
                },
                {
                    "status_code": status.HTTP_200_OK,
                    "body": [
                        {"code": "PHP", "description": "Philippine Peso"},
                        {"code": "USD", "description": "US Dollar"},
                    ]
                }
            ),
            (  # failed query to ext api test case:
                {
                    "ext_api_status_code": status.HTTP_404_NOT_FOUND,
                },
                {
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "body": []
                }
            ),
            (  # no supported symbols test case:
                {
                    "ext_api_status_code": status.HTTP_200_OK,
                    "ext_api_body": {
                        "success": False,
                        "symbols": {},
                    },
                },
                {
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "body": []
                }
            ),
        ]
    )
    def test__get(self, test_data, expected_results):
        mock_currencies_resp = mock()
        mock_currencies_resp.text = json.dumps(test_data.get("ext_api_body"))
        mock_currencies_resp.status_code = test_data["ext_api_status_code"]
        when(requests).get(
            url=f"{app_settings.exchange_rate_host}/symbols",
        ).thenReturn(mock_currencies_resp)

        response = self.client.get(f"/{self.version}/supported-currencies")
        assert expected_results["status_code"] == response.status_code
        assert expected_results["body"] or None == json.loads(response.text).get(
            "supported_currencies"
        )
