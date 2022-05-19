import json
import os
from typing import Dict
import pytest
from app.main import app
from app.utils import generate_signature, filter_equal
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def headers(signature) -> Dict:
    return {"bob-signature": signature}


@pytest.fixture
def signature(employee_created_event_payload) -> str:
    return generate_signature(
        json.dumps(employee_created_event_payload).encode("utf-8")
    )


@pytest.fixture
def new_employee_payload() -> Dict:
    return {
        "fullName": "Victor Ivanovich Yasinskiy",
        "creationDate": "2022-05-09",
        "displayName": "Victor Ivanovich Yasinskiy",
        "payroll": {
            "additionalPensionContribution": None,
            "nin": None,
            "timeSinceLastSalaryChange": None,
            "salary": {
                "monthlyPayment": None,
                "payPeriod": None,
                "yearlyPayment": None,
                "payment": {"currency": None},
                "activeEffectiveDate": None,
                "payFrequency": None,
            },
            "taxCode": None,
            "employment": {
                "fte": 100,
                "type": None,
                "flsaCode": None,
                "contract": "Full time",
                "calendarId": None,
                "salaryPayType": None,
                "workingPattern": None,
                "activeEffectiveDate": "2022-05-09",
                "weeklyHours": 45,
                "siteWorkingPattern": {
                    "workingPatternType": "partial_week",
                    "days": {
                        "sunday": False,
                        "tuesday": True,
                        "wednesday": True,
                        "monday": True,
                        "friday": True,
                        "thursday": True,
                        "saturday": False,
                    },
                    "hoursPerDay": 9,
                },
            },
            "variable": {
                "Executive bonus": {
                    "companyPercent": None,
                    "amount": None,
                    "paymentPeriod": None,
                    "individualPercent": None,
                    "departmentPercent": None,
                },
                "Bonus": {
                    "companyPercent": None,
                    "amount": None,
                    "paymentPeriod": None,
                    "individualPercent": None,
                    "departmentPercent": None,
                },
                "Commission": {
                    "companyPercent": None,
                    "amount": None,
                    "paymentPeriod": None,
                    "individualPercent": None,
                    "departmentPercent": None,
                },
            },
        },
        "address": {
            "siteAddress1": None,
            "city": None,
            "sitePostalCode": None,
            "line2": None,
            "country": None,
            "line1": None,
            "zipCode": None,
            "fullAddress": "     ",
            "siteCountry": "United Kingdom",
            "usaState": None,
            "siteState": None,
            "siteCity": None,
            "siteAddress2": None,
            "activeEffectiveDate": None,
            "postCode": None,
        },
        "peopleAnalytics": {
            "teamSizeRiskIndicator": "someRisk",
            "yearsWithCurrentTitleRiskIndicator": "noRisk",
            "tenureRankRiskIndicator": "atRisk",
            "lowRiskCounter": 5,
            "timeoffFrequencyRiskIndicator": "noRisk",
            "atRiskCounter": 2,
            "kidsRiskIndicator": "someRisk",
            "numOfDirectReportsRiskIndicator": "unknownRisk",
            "isManagerRiskIndicator": "someRisk",
            "yearsWithRecentSalaryRiskIndicator": "unknownRisk",
            "someRiskCounter": 3,
            "teamRecentTurnoverRiskIndicator": "noRisk",
            "ageRiskIndicator": "unknownRisk",
            "recentManagerChangeRiskIndicator": "noRisk",
            "managerTenureRiskIndicator": "atRisk",
            "numWithSameTitleRiskIndicator": "noRisk",
        },
        "state": "uninvited",
        "personal": {
            "shortBirthDate": None,
            "pronouns": None,
            "communication": {"skypeUsername": None, "slackUsername": None},
            "honorific": None,
            "nationality": ["Afghan", "Ukrainian"],
            "age": None,
            "birthDate": None,
        },
        "creationDateTime": "2022-05-09T07:36:42.293149",
        "work": {
            "shortStartDate": "05-09",
            "startDate": "2022-05-09",
            "manager": "2693707360307774170",
            "workPhone": None,
            "tenureDuration": {
                "periodISO": "P2D",
                "sortFactor": 2,
                "humanize": "2 days",
            },
            "custom": {"field_1644932887286": None},
            "durationOfEmployment": {
                "periodISO": "P2D",
                "sortFactor": 2,
                "humanize": "2 days",
            },
            "reportsToIdInCompany": None,
            "employeeIdInCompany": None,
            "reportsTo": {
                "displayName": "Indrek Truu",
                "email": "indrek.truu@tehops.io",
                "surname": "Truu",
                "firstName": "Indrek",
                "id": "2693707360307774170",
            },
            "workMobile": None,
            "indirectReports": None,
            "department": "Accounting",
            "siteId": 1814407,
            "tenureYears": 0,
            "customColumns": {
                "column_1639496202710": "228075491",
                "column_1644933593840": "Heathmont OU",
                "column_1639495541396": None,
            },
            "isManager": False,
            "title": "Business Development Manager",
            "site": "London (Demo)",
            "activeEffectiveDate": "2022-05-09",
            "directReports": None,
            "secondLevelManager": "2693707382730523368",
            "daysOfPreviousService": 0,
            "yearsOfService": 0.003,
        },
        "internal": {
            "periodSinceTermination": None,
            "yearsSinceTermination": None,
            "terminationReason": None,
            "probationEndDate": None,
            "currentActiveStatusStartDate": "2022-05-09",
            "terminationDate": None,
            "status": "Active",
            "terminationType": None,
            "notice": None,
            "lifecycleStatus": "employed",
        },
        "avatarUrl": None,
        "emergency": {
            "city": None,
            "address": None,
            "relation": None,
            "country": None,
            "mobilePhone": None,
            "secondName": None,
            "email": None,
            "surname": None,
            "firstName": None,
            "phone": None,
            "postCode": None,
        },
        "secondName": "Ivanovich",
        "eeo": {"ethnicity": None, "jobCategory": None},
        "about": {
            "foodPreferences": [],
            "socialData": {"linkedin": None, "twitter": None, "facebook": None},
            "superpowers": [],
            "hobbies": [],
            "about": None,
            "avatar": "https://images.hibob.com/default-avatars/VY_48.png",
        },
        "companyId": 475308,
        "email": "victor.yasinskiy@techops.com",
        "surname": "Yasinskiy",
        "identification": {"ssn": None, "ssnSerialNumber": None},
        "home": {
            "familyStatus": None,
            "mobilePhone": None,
            "privateEmail": None,
            "legalGender": None,
            "privatePhone": None,
            "numberOfKids": 0,
            "spouse": {
                "shortBirthDate": None,
                "gender": None,
                "birthDate": None,
                "surname": None,
                "firstName": None,
            },
        },
        "financial": {
            "iban": None,
            "bankName": None,
            "routingNumber": None,
            "swift": None,
            "rightToWorkExpiryDate": None,
            "identificationNumber": None,
            "passportNumber": None,
            "accountnumber": None,
            "bankAddress": None,
            "bankAccountType": None,
            "accountType": None,
            "sortcode": None,
            "accountName": None,
        },
        "humanReadable": {
            "fullName": "Victor Ivanovich Yasinskiy",
            "creationDate": "05/09/2022",
            "displayName": "Victor Ivanovich Yasinskiy",
            "payroll": {
                "salary": {"payment": ""},
                "employment": {
                    "fte": "100.00",
                    "contract": "Full time",
                    "activeEffectiveDate": "05/09/2022",
                    "weeklyHours": "45.00",
                    "siteWorkingPattern": "Monday,Tuesday,Wednesday,Thursday,Friday",
                },
            },
            "address": {"fullAddress": "     ", "siteCountry": "United Kingdom"},
            "peopleAnalytics": {
                "teamSizeRiskIndicator": "Some risk",
                "yearsWithCurrentTitleRiskIndicator": "Low risk",
                "tenureRankRiskIndicator": "At risk",
                "lowRiskCounter": "5",
                "timeoffFrequencyRiskIndicator": "Low risk",
                "atRiskCounter": "2",
                "kidsRiskIndicator": "Some risk",
                "numOfDirectReportsRiskIndicator": "N/A",
                "isManagerRiskIndicator": "Some risk",
                "yearsWithRecentSalaryRiskIndicator": "N/A",
                "someRiskCounter": "3",
                "teamRecentTurnoverRiskIndicator": "Low risk",
                "ageRiskIndicator": "N/A",
                "recentManagerChangeRiskIndicator": "Low risk",
                "managerTenureRiskIndicator": "At risk",
                "numWithSameTitleRiskIndicator": "Low risk",
            },
            "personal": {"nationality": "Afghan,Ukrainian"},
            "state": "Uninvited",
            "creationDateTime": "2022-05-09T07:36:42.293149",
            "work": {
                "shortStartDate": "05/09",
                "startDate": "05/09/2022",
                "manager": "Indrek Truu",
                "tenureDuration": "2 days",
                "durationOfEmployment": "2 days",
                "reportsTo": "Indrek Truu",
                "department": "Accounting",
                "siteId": "London (Demo)",
                "tenureYears": "0",
                "customColumns": {
                    "column_1639496202710": "Four4",
                    "column_1644933593840": "A1 company",
                },
                "isManager": "No",
                "title": "Business Development Manager",
                "site": "London (Demo)",
                "activeEffectiveDate": "05/09/2022",
                "secondLevelManager": "Alan Tullin",
                "daysOfPreviousService": "0",
                "yearsOfService": "0.003",
            },
            "internal": {
                "currentActiveStatusStartDate": "05/09/2022",
                "status": "Active",
                "lifecycleStatus": "Employed",
            },
            "secondName": "Ivanovich",
            "about": {
                "foodPreferences": "",
                "superpowers": "",
                "hobbies": "",
                "avatar": "https://images.hibob.com/default-avatars/VY_48.png",
            },
            "companyId": "475308",
            "email": "victor.yasinskiy@techops.com",
            "surname": "Yasinskiy",
            "home": {"numberOfKids": "0"},
            "id": "2834190035467633537",
            "firstName": "Victor",
        },
        "firstName": "Victor",
        "id": "2834190035467633537",
    }


@pytest.fixture
def employee_created_event_payload() -> Dict:
    payload: Dict = {
        "companyId": 475308,
        "employee": {
            "id": "2834190035467633537",
            "companyId": 475308,
            "firstName": "Victor",
            "surname": "Yasinskiy",
            "email": "victor.yasinskiy@techops.com",
            "displayName": "Victor Ivanovich Yasinskiy",
            "site": "London (Demo)",
            "siteId": 1814407,
        },
        "changedBy": {
            "id": "2821255344859119913",
            "companyId": 475308,
            "firstName": "Vladislav",
            "surname": "Kislitsyn",
            "email": "vk_admin@tehops.io",
            "displayName": "Vladislav Kislitsyn",
            "site": "New York (Demo)",
            "siteId": 1814408,
        },
        "type": "employee.created",
        "data": {
            "displayName": "Victor Ivanovich Yasinskiy",
            "personal": {
                "shortBirthDate": None,
                "pronouns": None,
                "honorific": None,
                "nationality": ["Afghan", "Ukrainian"],
            },
            "work": {
                "startDate": "2022-05-09",
                "shortStartDate": "05-09",
                "manager": "2693707360307774170",
                "workPhone": None,
                "tenureDuration": {
                    "periodISO": "P1D",
                    "sortFactor": 1,
                    "humanize": "1 day",
                },
                "custom": {"field_1644932887286": None},
                "reportsToIdInCompany": None,
                "durationOfEmployment": None,
                "employeeIdInCompany": None,
                "reportsTo": {
                    "displayName": "Indrek Truu",
                    "email": "indrek.truu@tehops.io",
                    "surname": "Truu",
                    "firstName": "Indrek",
                    "id": "2693707360307774170",
                },
                "workMobile": None,
                "indirectReports": None,
                "department": "Accounting",
                "siteId": 1814407,
                "tenureYears": 0,
                "customColumns": {
                    "column_1639496202710": "228075491",
                    "column_1644933593840": "Heathmont OU",
                    "column_1639495541396": None,
                },
                "isManager": False,
                "title": "Business Development Manager",
                "site": "London (Demo)",
                "activeEffectiveDate": "2022-05-09",
                "directReports": None,
                "secondLevelManager": "2693707382730523368",
                "yearsOfService": 0,
                "daysOfPreviousService": None,
            },
            "companyId": 475308,
            "about": {
                "foodPreferences": [],
                "socialData": {"linkedin": None, "twitter": None, "facebook": None},
                "hobbies": [],
                "superpowers": [],
                "about": None,
                "avatar": "https://images.hibob.com/default-avatars/VY_48.png",
            },
            "email": "victor.yasinskiy@techops.com",
            "surname": "Yasinskiy",
            "home": {"privateEmail": None},
            "id": "2834190035467633537",
            "firstName": "Victor",
        },
        "previous": None,
        "creationDate": "2022-05-09T07:36:42.486",
    }
    return payload

@pytest.fixture
def auth_token_payload_cmdbuild() -> Dict:
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
def employee_payload_cmdbuild() -> Dict:
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
        ]
    }
    return employee_payload


@pytest.fixture
def cmdb_employee_payload() -> Dict:
    return {
        'success': True,
        'data': [],
        'meta': {
            'total': 0
            }
        }

@pytest.fixture
def cmdb_manager_payload() -> Dict:
    return {
        'success': True,
        'data': [{'_id': 8681}],
        'meta': {
            'total': 1
            }
        }

@pytest.fixture
def cmdb_ou_payload() -> Dict:
    return {
	    'success': True,
	    'data': [{'_id': 86883}],
	    'meta': {'total': 1}
    }

@pytest.fixture
def cmdb_company_payload() -> Dict:
    return {
	    'success': True,
	    'data': [
	    	{
	    		'_id': 86786,
	    		'_type': 'Customer',
	    		'_user': 'admin',
	    		'__user_description': 'admin',
	    		'_beginDate': '2022-04-12T11:25:39.311548Z',
	    		'Code': None,
	    		'Description': 'Heathmont OU',
	    		'Notes': None,
	    		'CompanyTitle': 'Heathmont OÜ',
	    		'Address': None,
	    		'Postcode': None,
	    		'City': None,
	    		'Region': None,
	    		'Country': None,
	    		'Phone': None,
	    		'Fax': None,
	    		'Email': None,
	    		'Website': None
	    	}
	    ],
	    'meta': {'total': 1}
    }

###########
def test_create_employee_event(
    httpx_mock,
    client,
    headers,
    new_employee_payload,
    auth_token_payload_cmdbuild,
    employee_created_event_payload,
    cmdb_employee_payload,
    cmdb_ou_payload,
    cmdb_company_payload,
    cmdb_manager_payload,
):
    """
    Test employee creation in hibob
    """
    employee_id: str = employee_created_event_payload["employee"]["id"]
    httpx_mock.add_response(
        method="GET",
        url=f"https://api.hibob.com/v1/people/{employee_id}?includeHumanReadable=true",
        json=new_employee_payload,
    )
    httpx_mock.add_response(
        method="POST",
        url="https://52.49.159.189/ready2use-2.2-3.4/services/rest/v3/sessions?scope=service&returnId=true",
        json=auth_token_payload_cmdbuild,
    )
    employee_email: str = employee_created_event_payload["employee"]["email"]
    httpx_mock.add_response(
        method="GET",
        url=f"""https://52.49.159.189/ready2use-2.2-3.4/services/rest/v3/classes/InternalEmployee/cards?filter={filter_equal("Email", employee_email)}""",
        json=cmdb_employee_payload
    )
    o_u: str = "Accounting"
    httpx_mock.add_response(
        method="GET",
        url=f"""https://52.49.159.189/ready2use-2.2-3.4/services/rest/v3/classes/OU/cards?filter={filter_equal("Name", o_u)}""",
        json=cmdb_ou_payload,
    )
    manager_email: str = employee_created_event_payload["data"]["work"]["reportsTo"]["email"]
    httpx_mock.add_response(
        method="GET",
        url=f"""https://52.49.159.189/ready2use-2.2-3.4/services/rest/v3/classes/InternalEmployee/cards?filter={filter_equal("Email", manager_email)}""",
        json=cmdb_manager_payload
    )
    company: str = "A1 company"
    httpx_mock.add_response(
        method="GET",
        url=f"""https://52.49.159.189/ready2use-2.2-3.4/services/rest/v3/classes/Customer/cards?filter={filter_equal("CompanyTitle", company)}""",
        json=cmdb_company_payload,
    )
    httpx_mock.add_response(
        method="POST",
        url="https://52.49.159.189/ready2use-2.2-3.4/services/rest/v3/classes/InternalEmployee/cards",
        json={'success': True},
    )
    response = client.post(
        "/webhook/", json=employee_created_event_payload, headers=headers
    )
    assert response.status_code == 200
