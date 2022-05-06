from typing import Dict
import pytest
import httpx
from app.utils import generate_cmdbuild_token, EmployeeInitialContext
from pytest_httpx import HTTPXMock


@pytest.mark.asyncio
async def test_generate_cmdbuild_token(httpx_mock: HTTPXMock):
    """
    Function tests helper function what generates CMDBuild authorization token
    """
    content: Dict = {
        "success": True,
        "data": {
            "_id": "g1i77zdg2xxha8kn6mcoap9p",
            "username": "admin",
            "password": "qwerty",
        },
    }
    httpx_mock.add_response(
        method="POST",
        url="https://locahost/ready2use-2.2-3.4/services/rest/v3/sessions?scope=service&returnId=true",
        json=content,
    )
    async with httpx.AsyncClient(verify=False) as client:
        token: str = await generate_cmdbuild_token(
            client=client,
            url="https://locahost/ready2use-2.2-3.4/services",
            username="admin",
            password="qwerty",
        )
        assert token == content["data"]["_id"]


class TestEmployeeInitialContext:

    @pytest.fixture
    def cmdbuild_employee_payload(self) -> Dict:
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
                    'ReportsTo': None
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
                    'ReportsTo': 6053
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
                    'ReportsTo': 6087
                },
            ],
        }
        return employee_payload

    @pytest.fixture
    def hr_system_employee_payload(self) -> Dict:
        employee_payload: Dict = {
            'employees': [
                # Alan Tullin
                # Handles cases:
                # - New employee
                # - New company
                # - New department
                {
                    'work': {
                        'reportsTo': {}, # has no manager
                    },
                    'humanReadable': {
                        'fullName': 'Alan George Tullin',
                        'displayName': 'Alan Tullin',
                        'state': 'Uninvited',
                        'work': {
                            'reportsTo': 'Frederick Bateson',
                            'department': 'Management',
                            'customColumns': {'column_1620839439167': 'Trust Holding'},
                            'isManager': 'Yes',
                            'title': 'General Manager',
                        },
                        'secondName': 'George',
                        'email': 'alan.tullin@tehops.io',
                        'surname': 'Tullin',
                        'id': '2693707382730523368',
                        'firstName': 'Alan'
                        },
                },
                # Holding John
                # Handles cases:
                # - CMDBuild pointed wrong surname
                # - Changed ReportsTo new employee Alan Tullin
                {
                    'work': {
                        'reportsTo': {
                            'email': 'alan.tullin@tehops.io',
                        },
                    },
                    'humanReadable': {
                        'fullName': 'HoldingTEST John',
                        'displayName': 'HoldingTEST John',
                        'state': 'Uninvited',
                        'work': {
                            'reportsTo': 'Alan Tullin',
                            'department': 'Development',
                            'customColumns': {'column_1620839439167': 'Softline'},
                            'isManager': 'Yes',
                            'title': 'Line Manager',
                        },
                        'email': 'j.holding@example.com',
                        'surname': 'HoldingTEST',
                        'id': '2652401818839023638',
                        'firstName': 'John'
                        },
                },
                # Colding Connad
                {
                    'work': {
                        'reportsTo': {
                            'email': 'j.holding@example.com',
                        },
                    },
                    'humanReadable': {
                        'fullName': 'Colding Connad',
                        'displayName': 'Colding Connad',
                        'state': 'Uninvited',
                        'work': {
                            'department': 'Development',
                            'customColumns': {'column_1620839439167': 'Softline'},
                            'isManager': 'Yes',
                            'title': 'Erlang Developer',
                        },
                        #'secondName': 'George',
                        'email': 'c.colding@example.com',
                        'surname': 'Colding',
                        'id': '2572113413220074039',
                        'firstName': 'Connad'
                        },
                },
                # Smith Tom
                # Handles cases:
                # - ReportTo field changed from Colding Connad to Holding John
                {
                    'work': {
                        'reportsTo': {
                            'email': 'j.holding@example.com',
                        },
                    },
                    'humanReadable': {
                        'fullName': 'Smith Tom',
                        'displayName': 'Smith Tom',
                        'state': 'Uninvited',
                        'work': {
                            'department': 'Development',
                            'customColumns': {'column_1620839439167': 'Softline'},
                            'isManager': 'No',
                            'title': 'QA',
                        },
                        #'secondName': 'George',
                        'email': 't.smith@example.com',
                        'surname': 'Smith',
                        'id': '2572113575690633946',
                        'firstName': 'Tom'
                        },
                },
            ]
        }
        return employee_payload


    @pytest.mark.asyncio
    async def test_create_departments_cards(self, httpx_mock: HTTPXMock):
        pass
    
    @pytest.mark.asyncio
    async def test_create_company_cards(self, httpx_mock: HTTPXMock):
        pass
    
    @pytest.mark.asyncio   
    async def _update_employee_card(self, httpx_mock: HTTPXMock):
        pass

    @pytest.mark.asyncio
    async def test_fetch_employees_from_hr_system(
        self,
        hr_system_employee_payload: Dict,
        httpx_mock: HTTPXMock
    ):
        httpx_mock.add_response(
            method="GET",
            url="https://api.hibob.com/v1/people?showInactive=false&includeHumanReadable=true",
            json=hr_system_employee_payload,
        )
        employee_context = EmployeeInitialContext(
            bob_token="",
            username_cmdbuild="admin",
            password_cmdbuild="qwerty",
            cmdbuild_url="https://locahost/ready2use-2.2-3.4/services",
            bob_url="https://api.hibob.com/v1/people?showInactive=false&includeHumanReadable=true",
        )
        await employee_context._fetch_employees_from_hr_system()


    @pytest.mark.asyncio
    async def test_fetch_employees_from_cmdbuild(self, cmdbuild_employee_payload, httpx_mock: HTTPXMock):

        token_payload: Dict = {
            "success": True,
            "data": {
                "_id": "g1i77zdg2xxha8kn6mcoap9p",
                "username": "admin",
                "password": "qwerty",
            },
        }

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

        httpx_mock.add_response(
            method="POST",
            url="https://locahost/ready2use-2.2-3.4/services/rest/v3/sessions?scope=service&returnId=true",
            json=token_payload,
        )

        httpx_mock.add_response(
            method="GET",
            url="https://locahost/ready2use-2.2-3.4/services/rest/v3/classes/InternalEmployee/cards",
            json=cmdbuild_employee_payload,
        )

        httpx_mock.add_response(
            method="GET",
            url="https://locahost/ready2use-2.2-3.4/services/rest/v3/classes/Customer/cards",
            json=customer_payload,
        )

        httpx_mock.add_response(
            method="GET",
            url="https://locahost/ready2use-2.2-3.4/services/rest/v3/classes/OU/cards",
            json=ou_payload,
        )

        employee_context = EmployeeInitialContext(
            bob_token="",
            username_cmdbuild="admin",
            password_cmdbuild="qwerty",
            cmdbuild_url="https://locahost/ready2use-2.2-3.4/services",
            bob_url="https://api.hibob.com/v1/people?showInactive=false&includeHumanReadable=true",
        )
        employee_info_df = await employee_context._fetch_employees_from_cmdbuild()
