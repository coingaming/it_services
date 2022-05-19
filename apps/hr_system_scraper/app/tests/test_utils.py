from typing import Dict
import logging
from datetime import datetime
import json
import time
import pytest
import httpx
from app.utils import generate_signature, EmployeeInterSystemsContext, get_base_url
from pytest_httpx import HTTPXMock
from app.main import app
from app.utils import generate_signature
from fastapi.testclient import TestClient


class TestEmployeeInterSystemsContext:
    @pytest.fixture
    def logger(self):
        app_name: str = "hibob-webhook-listener-test"
        logger = logging.getLogger(app_name)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
        ts = datetime.utcfromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
        file_logging = logging.FileHandler(f"{app_name}-{ts}.log")
        file_logging.setFormatter(formatter)
        logger.addHandler(file_logging)
        return logger

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(app)

    @pytest.fixture
    def headers(self, signature) -> Dict:
        return {"bob-signature": signature}

    @pytest.fixture
    def signature(self, employee_created_event_payload) -> str:
        return generate_signature(
            json.dumps(employee_created_event_payload).encode("utf-8")
        )

    @pytest.fixture
    def customer_payload_cmdbuild(self) -> Dict:
        customer_payload: Dict = {
            "success": True,
            "data": [
                {
                    "_id": 18516846,
                    "Code": "524813",
                    "Description": "Softline",
                    "CompanyTitle": "Softline",
                }
            ],
        }
        return customer_payload

    @pytest.fixture
    def ou_payload_cmdbuild(self) -> Dict:
        ou_payload: Dict = {
            "success": True,
            "data": [
                {
                    "_id": 6067,
                    "Parent": None,
                    "Code": "Development_1",
                    "Notes": None,
                    "Description": "Development",
                    "Manager": 7887,
                    "Company": None,
                    "Name": "Quality Assurance",
                },
            ],
        }
        return ou_payload

    @pytest.fixture
    def auth_token_payload_cmdbuild(self) -> Dict:
        token_payload: Dict = {
            "success": True,
            "data": {
                "_id": "g1i77zdg2xxha8kn6mcoap9p",
                "username": "admin",
                "password": "qwerty",
            },
        }
        return token_payload

    @pytest.fixture
    def employee_payload_cmdbuild(self) -> Dict:
        employee_payload: Dict = {
            "success": "true",
            "data": [
                {
                    "_id": 6053,
                    "Code": "2652401818839023638",
                    "Description": "Holding John",
                    "Number": "IE0212",
                    "LastName": "Holding",
                    "FirstName": "John",
                    "Email": "j.holding@example.com",
                    "State": 108,
                    "Company": 18516846,
                    "OU": 6067,
                    "ReportsTo": None,
                },
                {
                    "_id": 6087,
                    "Code": "2572113413220074039",
                    "Description": "Colding Conrad",
                    "Number": "IE0212",
                    "LastName": "Colding",
                    "FirstName": "Conrad",
                    "Email": "c.colding@example.com",
                    "State": 108,
                    "Company": 18516846,
                    "OU": 6067,
                    "ReportsTo": 6053,
                },
                {
                    "_id": 6079,
                    "Code": "2572113575690633946",
                    "Description": "Smith Tom",
                    "Number": "IE0210",
                    "LastName": "Smith",
                    "FirstName": "Tom",
                    "Email": "t.smith@example.com",
                    "State": 108,
                    "Company": 18516846,
                    "OU": 6067,
                    "ReportsTo": 6087,
                },
            ],
        }
        return employee_payload

    @pytest.fixture
    def config(self) -> Dict:
        return {
            "debug": True,
            "cmdbuild": {"url": {"debug": "https://localhost/ready2use-2.2-3.4/services", "prod": None}},
            "hr_system": {"url": {"debug": "https://api.hibob.com/v1", "prod": None}},
        }

    @pytest.fixture
    def hr_system_employee_payload(self) -> Dict:
        employee_payload: Dict = {
            "employees": [
                # Alan Tullin
                # Handles cases:
                # - New employee
                # - New company
                # - New department
                {
                    "work": {
                        "reportsTo": None,  # has no manager
                    },
                    "humanReadable": {
                        "fullName": "Alan George Tullin",
                        "displayName": "Alan Tullin",
                        "state": "Uninvited",
                        "work": {
                            "reportsTo": "Frederick Bateson",
                            "department": "Management",
                            "customColumns": {"column_1620839439167": "Trust Holding"},
                            "isManager": "Yes",
                            "title": "General Manager",
                        },
                        "secondName": "George",
                        "email": "alan.tullin@tehops.io",
                        "surname": "Tullin",
                        "id": "2693707382730523368",
                        "firstName": "Alan",
                    },
                },
                # Holding John
                # Handles cases:
                # - CMDBuild pointed wrong surname
                # - Changed ReportsTo new employee Alan Tullin
                {
                    "work": {
                        "reportsTo": {
                            "email": "alan.tullin@tehops.io",
                        },
                    },
                    "humanReadable": {
                        "fullName": "HoldingTEST John",
                        "displayName": "HoldingTEST John",
                        "state": "Uninvited",
                        "work": {
                            "reportsTo": "Alan Tullin",
                            "department": "Development",
                            "customColumns": {"column_1620839439167": "Softline"},
                            "isManager": "Yes",
                            "title": "Line Manager",
                        },
                        "email": "j.holding@example.com",
                        "surname": "HoldingTEST",
                        "id": "2652401818839023638",
                        "firstName": "John",
                    },
                },
                # Colding Connad
                {
                    "work": {
                        "reportsTo": {
                            "email": "j.holding@example.com",
                        },
                    },
                    "humanReadable": {
                        "fullName": "Colding Connad",
                        "displayName": "Colding Connad",
                        "state": "Uninvited",
                        "work": {
                            "department": "Development",
                            "customColumns": {"column_1620839439167": "Softline"},
                            "isManager": "Yes",
                            "title": "Erlang Developer",
                        },
                        #'secondName': 'George',
                        "email": "c.colding@example.com",
                        "surname": "Colding",
                        "id": "2572113413220074039",
                        "firstName": "Connad",
                    },
                },
                # Smith Tom
                # Handles cases:
                # - ReportTo field changed from Colding Connad to Holding John
                {
                    "work": {
                        "reportsTo": {
                            "email": "j.holding@example.com",
                        },
                    },
                    "humanReadable": {
                        "fullName": "Smith Tom",
                        "displayName": "Smith Tom",
                        "state": "Uninvited",
                        "work": {
                            "department": "Development",
                            "customColumns": {"column_1620839439167": "Softline"},
                            "isManager": "No",
                            "title": "QA",
                        },
                        #'secondName': 'George',
                        "email": "t.smith@example.com",
                        "surname": "Smith",
                        "id": "2572113575690633946",
                        "firstName": "Tom",
                    },
                },
            ]
        }
        return employee_payload

    @pytest.mark.asyncio
    async def test_get_employees_from_hr_system(
        self,
        hr_system_employee_payload: Dict,
        httpx_mock: HTTPXMock,
        config: Dict,
        logger
    ):
        httpx_mock.add_response(
            method="GET",
            url="https://api.hibob.com/v1/people?showInactive=false&includeHumanReadable=true",
            json=hr_system_employee_payload,
        )
        cmdbuild_http_client = httpx.AsyncClient(verify=False)
        bob_http_client = httpx.AsyncClient()

        async with (
            httpx.AsyncClient(
                base_url=get_base_url(config, "cmdbuild")
            ) as cmdbuild_http_client,
            httpx.AsyncClient(
                base_url=get_base_url(config, "hr_system")
            ) as bob_http_client,
        ):
            employee_context = EmployeeInterSystemsContext(
                bob_http_client=bob_http_client,
                cmdbuild_http_client=cmdbuild_http_client,
                logger=logger
            )
            await employee_context._get_all_bob_employees()

    @pytest.mark.asyncio
    async def test_get_all_cmdb_employees_from_cmdb(
        self,
        employee_payload_cmdbuild: Dict,
        auth_token_payload_cmdbuild: Dict,
        customer_payload_cmdbuild: Dict,
        ou_payload_cmdbuild: Dict,
        logger,
        config: Dict,
        httpx_mock: HTTPXMock,
    ):
        httpx_mock.add_response(
            method="POST",
            url="https://localhost/ready2use-2.2-3.4/services/rest/v3/sessions?scope=service&returnId=true",
            json=auth_token_payload_cmdbuild,
        )
        httpx_mock.add_response(
            method="GET",
            url="https://localhost/ready2use-2.2-3.4/services/rest/v3/classes/InternalEmployee/cards",
            json=employee_payload_cmdbuild,
        )
        httpx_mock.add_response(
            method="GET",
            url="https://localhost/ready2use-2.2-3.4/services/rest/v3/classes/Customer/cards",
            json=customer_payload_cmdbuild,
        )
        httpx_mock.add_response(
            method="GET",
            url="https://localhost/ready2use-2.2-3.4/services/rest/v3/classes/OU/cards",
            json=ou_payload_cmdbuild,
        )

        async with (
            httpx.AsyncClient(
                base_url=get_base_url(config, "cmdbuild")
            ) as cmdbuild_http_client,
            httpx.AsyncClient(
                base_url=get_base_url(config, "hr_system")
            ) as bob_http_client,
        ):
            employee_context = EmployeeInterSystemsContext(
                bob_http_client=bob_http_client,
                cmdbuild_http_client=cmdbuild_http_client,
                logger=logger
            )
            await employee_context._get_all_cmdb_employees_from_cmdb()