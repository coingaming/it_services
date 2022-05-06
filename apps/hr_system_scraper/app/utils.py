import asyncio
import os
import base64
import hmac
import hashlib
from typing import Dict, Any, List, Tuple
from dataclasses import make_dataclass, field, fields
from pathlib import Path
import yaml
import httpx
import pandas as pd


def load_config(path: str) -> Any:
    """Return downloaded yml config, which is specified app configuration
    For instance: host, port and e.t.c

    >>> from pathlib import Path, PosixPath
    >>> PROJECT_ROOT: PosixPath = Path(__file__).parent.parent
    >>> config: Dict = load_config(PROJECT_ROOT / "configs" / "base.yml")
    >>> isinstance(config, dict)
    True
    """
    with Path(path).open(encoding="utf-8") as file:
        return yaml.safe_load(file.read())


def read_env_variable(variable: str) -> Any:
    """Return specified environment variable

    >>> os.environ["TOKEN"] = "TEST_TOKEN123"
    >>> var: str = read_env_variable("TOKEN")
    >>> var
    'TEST_TOKEN123'
    """
    value: Any = os.environ.get(variable)
    if value is None:
        raise RuntimeError(f"{variable} is required to start the service!")
    return value


def verify_signature(received_signature: str, payload: bytes) -> bool:
    """
    Helper-function to generate the signature to verify reqiest from hibob
    """
    webhook_secret: str = os.environ.get("BOB_SECRET_KEY")
    digest = hmac.new(webhook_secret.encode("utf-8"), payload, hashlib.sha512).digest()
    calculated_signature: str = base64.b64encode(digest).decode()
    return hmac.compare_digest(calculated_signature, received_signature)


async def make_get_request(client: httpx.AsyncClient, url: str, headers: Dict) -> Dict:
    """
    Helper-function to make async GET request with httpx client
    """
    response: httpx.Response = await client.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


async def generate_cmdbuild_token(
    url: str, username: str, password: str, client: httpx.AsyncClient
) -> str:
    """
    Helper-function to generate authorization token
    Every request requires the user to specify in the header the field 'Cmdbuild-authorization'
    >>> import httpx
    >>> import asyncio
    >>> url: str = "https://52.49.159.189/ready2use-2.2-3.4/services"
    >>> username: str = "admin"
    >>> password: str = ""
    >>> client: httpx.AsyncClient = httpx.AsyncClient(verify=False)
    >>> token: str = asyncio.run(generate_cmdbuild_token(url, username, password, client))
    >>> isinstance(token, str)
    True
    """
    path: str = "rest/v3/sessions?scope=service&returnId=true"
    response: httpx.Response = await client.post(
        f"{url}/{path}", json={"username": username, "password": password}
    )
    response.raise_for_status()
    response_payload: Dict = response.json()
    token: str = response_payload["data"]["_id"]
    return token


class EmployeeInitialContext:
    """
    Reduces information about employees to a common denominator between 2 systems:
    hr and cmdbuild.
    We believe that the most relevant data is in the hr system.
    Public API 'prepare' fetches data from hr system and propogate all the changes to cmdbuild.

    Class atrributes:
    bob_custom_company_column_id : str
    cmdbuild_compatible_nan : str

    Instance variables:
    cmdbuild_url: str,
    bob_url: str,
    cmdbuild_client: httpx.AsyncClient,
    bob_client: httpx.AsyncClient,
    bob_token: str,
    _cmdbuild_token: str,
    username_cmdbuild: str,
    password_cmdbuild: str,
    employee_card_id_by_email: Dict,
    employee_email_by_card_id: Dict,
    company_name_by_card_id: Dict,
    company_card_id_by_name: Dict,
    department_card_id_by_name: Dict,
    department_name_by_card_id: Dict,
    lock_cmdbuild_token: asyncio.Lock

    """

    bob_custom_company_column_id: str = "column_1620839439167"
    cmdbuild_compatible_nan: str = "nan"
    InternalEmployee = make_dataclass(
        "InternalEmployee",
        [
            ("Code", str),
            ("FirstName", str),
            ("MiddleName", str),
            ("LastName", str),
            ("DisplayName", str),
            ("FullName", str),
            ("IsManager", bool),
            ("Email", str),
            ("ReportsTo", str),
            ("JobTitle", str),
            ("Department", str),
            ("Company", str),
            ("CardId", int, field(default=None)),
        ],
    )

    def __init__(
        self,
        bob_token: str,
        username_cmdbuild: str,
        password_cmdbuild: str,
        cmdbuild_url: str,
        bob_url: str,
    ):

        self.cmdbuild_url: str = cmdbuild_url
        self.bob_url: str = bob_url
        self.cmdbuild_client: httpx.AsyncClient = httpx.AsyncClient(verify=False)
        self.bob_client: httpx.AsyncClient = httpx.AsyncClient()
        self.bob_token: str = bob_token
        self._cmdbuild_token: str = None
        self.username_cmdbuild: str = username_cmdbuild
        self.password_cmdbuild: str = password_cmdbuild
        self.employee_card_id_by_email: Dict = {}
        self.employee_email_by_card_id: Dict = {}
        self.company_name_by_card_id: Dict = {}
        self.company_card_id_by_name: Dict = {}
        self.department_card_id_by_name: Dict = {}
        self.department_name_by_card_id: Dict = {}
        self.lock_cmdbuild_token = asyncio.Lock()

    async def prepare(self):
        """
        The main API method.
        Fetches data from both hr system and cmdbuild.
        Based on the fact that hr system contains actual information
        Propogates it to cmdbuild
        """
        employee_fetch_result: List[Dict] = await asyncio.gather(
            self._fetch_employees_from_hr_system(),
            self._fetch_employees_from_cmdbuild(),
        )
        bob_sfx: str = "_bob"
        cmdbuild_sfx: str = "_cmdbuild"
        prepared_employees_df: pd.DataFrame = self._prepare_employees_info(
            *employee_fetch_result, suffixes=(bob_sfx, cmdbuild_sfx)
        )
        await asyncio.gather(
            self._create_departments_cards(
                departments=prepared_employees_df["Department_bob"].unique()
            ),
            self._create_company_cards(
                companies=prepared_employees_df["Company_bob"].unique()
            ),
            self._create_employee_card(
                employees_df=prepared_employees_df.query(
                    f"CardId_cmdbuild == '{EmployeeInitialContext.cmdbuild_compatible_nan}'"
                ),
                suffixes=(bob_sfx, cmdbuild_sfx),
            ),
            self._update_employee_card(
                employees_df=prepared_employees_df.query(
                    f"CardId_cmdbuild != '{EmployeeInitialContext.cmdbuild_compatible_nan}'"
                ),
                suffixes=(bob_sfx, cmdbuild_sfx),
            ),
        )

    async def _get_cmdbuild_token(self):
        """
        Generates authentication token
        Which should be added in the header of the request
        https://www.cmdbuild.org/file/manuali/webservice-manual-in-english, Page 11
        """
        async with self.lock_cmdbuild_token:
            if self._cmdbuild_token is None:
                self._cmdbuild_token = await generate_cmdbuild_token(
                    url=self.cmdbuild_url,
                    username=self.username_cmdbuild,
                    password=self.password_cmdbuild,
                    client=self.cmdbuild_client,
                )
            return self._cmdbuild_token

    def _prepare_employees_info(
        self,
        bob_employees_df: pd.DataFrame,
        cmdbuild_employees_df: pd.DataFrame,
        suffixes: Tuple[str],
    ) -> pd.DataFrame:
        """
        Combines information from hr system and cmdbuild to easily manipulate
        """
        column_name_for_join: str = "Email"
        prepared_employees_df: pd.DataFrame = pd.merge(
            bob_employees_df,
            cmdbuild_employees_df,
            on=column_name_for_join,
            how="left",
            suffixes=suffixes,
        )
        prepared_employees_df.fillna(
            value=EmployeeInitialContext.cmdbuild_compatible_nan, inplace=True
        )
        return prepared_employees_df

    async def _fetch_employees_from_cmdbuild(self) -> pd.DataFrame:
        """
        Fetches ALL employee information from cmdbuild
        """
        requested_cards_types: Tuple[str] = ("Customer", "OU", "InternalEmployee")
        token = await self._get_cmdbuild_token()
        fetch_employee_info_from_cmdbuild_tasks: List[Dict] = [
            make_get_request(
                client=self.cmdbuild_client,
                url=f"{self.cmdbuild_url}/rest/v3/classes/{cardId}/cards",
                headers={"Cmdbuild-authorization": token},
            )
            for cardId in requested_cards_types
        ]
        result: List[Dict] = await asyncio.gather(
            *fetch_employee_info_from_cmdbuild_tasks
        )
        companies_info, organization_units_info, employees_info = result

        # update local caches
        for card in employees_info["data"]:
            email: str = card["Email"]
            card_id: str = card["_id"]
            self.employee_card_id_by_email[email] = card_id
            self.employee_email_by_card_id[card_id] = email

        for card in organization_units_info["data"]:
            card_id: str = card["_id"]
            name: str = card["Name"]
            self.department_card_id_by_name[name] = card_id
            self.department_name_by_card_id[card_id] = name

        for card in companies_info["data"]:
            card_id: str = card["_id"]
            descr: str = card["Description"]
            self.company_name_by_card_id[card_id] = descr
            self.company_card_id_by_name[descr] = card_id

        cmdbuild_employees: List[self.InternalEmployee] = []
        for employee in employees_info["data"]:
            match employee:
                case {
                    "_id": card_id,
                    "Code": code,
                    "FirstName": first_name,
                    "MiddleName": middle_name,
                    "LastName": last_name,
                    "DisplayName": display_name,
                    "FullName": full_name,
                    "IsManager": is_manager,
                    "Email": email,
                    "ReportsTo": manager_card_id,
                    "JobTitle": job_title,
                    "OU": department_card_id,
                    "Company": company_card_id,
                }:
                    cmdbuild_employees.append(
                        self.InternalEmployee(
                            Code=code,
                            FirstName=first_name,
                            MiddleName=middle_name,
                            LastName=last_name,
                            DisplayName=display_name,
                            FullName=full_name,
                            IsManager=is_manager,
                            Email=email,
                            ReportsTo=self.employee_email_by_card_id.get(
                                manager_card_id
                            ),
                            JobTitle=job_title,
                            Department=self.department_name_by_card_id.get(
                                department_card_id
                            ),
                            Company=self.company_name_by_card_id.get(company_card_id),
                            CardId=card_id,
                        )
                    )
        return pd.DataFrame(cmdbuild_employees)

    async def _fetch_employees_from_hr_system(self) -> pd.DataFrame:
        """
        Method fetches ALL employee information from HR system (hibob)
        """
        bob_payload = await make_get_request(
            client=self.bob_client,
            url=self.bob_url,
            headers={"Accept": "application/json", "Authorization": self.bob_token},
        )

        bob_employees: List = []
        for employee in bob_payload["employees"]:
            match employee:
                case {
                    "work": {
                        "reportsTo": {"email": manager_email},
                    },
                    "humanReadable": human_readable,
                }:
                    work_info: Dict = human_readable["work"]
                    department: str = work_info.get("department")
                    is_manager: bool = work_info.get("isManager") == "Yes"
                    job_title: str = work_info.get("title")
                    company: str = work_info.get("customColumns", {}).get(
                        self.bob_custom_company_column_id
                    )  # column id from production hibob
                    code: str = human_readable.get("id")
                    first_name: str = human_readable.get("firstName")
                    middle_name: str = human_readable.get("middleName")
                    last_name: str = human_readable.get("surname")
                    display_name: str = human_readable.get("displayName")
                    full_name: str = human_readable.get("fullName")
                    email: str = human_readable.get("email")
                    bob_employees.append(
                        self.InternalEmployee(
                            Code=code,
                            FirstName=first_name,
                            MiddleName=middle_name,
                            LastName=last_name,
                            DisplayName=display_name,
                            FullName=full_name,
                            IsManager=is_manager,
                            Email=email,
                            ReportsTo=manager_email,
                            JobTitle=job_title,
                            Department=department,
                            Company=company,
                        )
                    )
        return pd.DataFrame(bob_employees)

    async def _update_cmdbuild_card(
        self, data: Dict, card_id: str, class_id: str
    ) -> int:
        """
        Helper method which does HTTP PUT to update existing card in cmdbuild
        """
        path: str = f"rest/v3/classes/{class_id}/cards/{card_id}"
        url: str = f"{self.cmdbuild_url}/{path}"
        token: str = await self._get_cmdbuild_token()
        response: httpx.Response = await self.cmdbuild_client.put(
            headers={"Cmdbuild-authorization": token}, url=url, json=data
        )
        response.raise_for_status()
        response_payload: Dict = response.json()
        assert response_payload["success"]
        return response_payload

    async def create_cmdbuild_card(self, class_id: str, data: str) -> Dict:
        """
        Helper method which does HTTP PUSH to create new card in cmdbuild
        """
        path: str = f"rest/v3/classes/{class_id}/cards"
        url: str = f"{self.cmdbuild_url}/{path}"
        token: str = await self._get_cmdbuild_token()
        response: httpx.Response = await self.cmdbuild_client.post(
            headers={"Cmdbuild-authorization": token}, url=url, json=data
        )
        response.raise_for_status()
        response_payload: Dict = response.json()
        assert response_payload["success"]
        return response_payload

    async def _create_company_cards(self, companies: List):
        """
        Creates new companies (Customer) cards in CMDBuild and update related caches
        """
        async_tasks: List = []
        for company in companies:
            if (
                company != EmployeeInitialContext.cmdbuild_compatible_nan
                and company not in self.company_card_id_by_name
            ):
                async_tasks.append(
                    self.create_cmdbuild_card(
                        class_id="Customer",
                        data={"Description": company, "CompanyTitle": company},
                    )
                )
        results: List[Dict] = await asyncio.gather(*async_tasks)
        # update caches
        for item_result in results:
            assert item_result["success"]
            data: Dict = item_result["data"]
            name: str = data["CompanyTitle"]
            card_id: str = data["_id"]
            self.company_card_id_by_name[name] = card_id
            self.company_name_by_card_id[card_id] = name

    async def _create_departments_cards(self, departments: List):
        """
        Creates new departments (OU) cards in CMDBuild and update related caches
        """
        async_tasks: List = []
        for department in departments:
            if (
                department != EmployeeInitialContext.cmdbuild_compatible_nan
                and department not in self.department_card_id_by_name
            ):
                async_tasks.append(
                    self.create_cmdbuild_card(
                        class_id="OU",
                        data={"Name": department, "Description": department},
                    )
                )
        results: List[Dict] = await asyncio.gather(*async_tasks)
        # update caches
        for item_result in results:
            assert item_result["success"]
            data: Dict = item_result["data"]
            name: str = data["Name"]
            _id: str = data["_id"]
            self.department_card_id_by_name[name] = _id
            self.department_name_by_card_id[_id] = name

    async def _update_employee_card(
        self, employees_df: pd.DataFrame, suffixes: Tuple[str]
    ):
        """
        Updates existing employee cards in cmdbuild
        """
        bob_sfx, cmdbuild_sfx = suffixes
        update_employees_async_tasks: List = []
        # by comparing fields below data diff is retrieving from hr system and cmdbuild
        fields_to_compare = [
            (f"{field.name}{bob_sfx}", f"{field.name}{cmdbuild_sfx}")
            for field in fields(EmployeeInitialContext.InternalEmployee)
            if field.name not in ["Email", "CardId"]
        ]
        for row in employees_df.itertuples():
            employee_attrs: Dict = {}
            employee_email: str = getattr(row, "Email")
            employee_card_id: str = self.employee_card_id_by_email[employee_email]

            for bob_field, cmdbuild_field in fields_to_compare:
                bob_attr: str = getattr(row, bob_field)
                cmdbuild_attr: str = getattr(row, cmdbuild_field)
                if (
                    bob_attr != cmdbuild_attr
                    and bob_attr != EmployeeInitialContext.cmdbuild_compatible_nan
                ):
                    match bob_field:
                        case "ReportsTo_bob":
                            value = self.employee_card_id_by_email[bob_attr]
                        case "Department_bob":
                            value = self.department_card_id_by_name[bob_attr]
                        case "Company_bob":
                            value = self.company_card_id_by_name[bob_attr]
                        case _:
                            value = bob_attr
                    employee_attrs[bob_field.removesuffix(bob_sfx)] = value

            if employee_attrs:
                update_employees_async_tasks.append(
                    self._update_cmdbuild_card(
                        data=employee_attrs,
                        card_id=employee_card_id,
                        class_id="InternalEmployee",
                    )
                )
        await asyncio.gather(*update_employees_async_tasks)

    async def _create_employee_card(
        self, employees_df: pd.DataFrame, suffixes: Tuple[str]
    ) -> int:
        """
        Creates new cmdbuild card for InternalEmployee class
        """
        bob_sfx, _ = suffixes
        create_employees_async_tasks: List = []
        for row in employees_df.itertuples():
            new_employee_attrs: Dict = {
                field.name: row[f"{field.name}{bob_sfx}"]
                for field in fields(EmployeeInitialContext.InternalEmployee)
                # Exclude next fields:
                # 'CardId' - is not an attribute in CMDBUILD;
                # 'ReportsTo' - Manage card may not exist yet.
                if field.name not in ["CardId", "ReportsTo"]
            }
            create_employees_async_tasks.append(
                self.create_cmdbuild_card(
                    class_id="InternalEmployee", data=new_employee_attrs
                )
            )
        results: List[Dict] = await asyncio.gather(*create_employees_async_tasks)
        # update local caches
        for item_result in results:
            data: Dict = item_result["data"]
            email: str = data["Email"]
            card_id: str = data["_id"]
            self.employee_card_id_by_email[email] = card_id

        # set managers for the newly created employee
        set_employee_manager_async_tasks: List = []
        for row in employees_df.itertuples():

            employee_email: str = row["Email"]
            employee_card_id: str = self.employee_card_id_by_email[employee_email]

            manager_email: str = row["ReportsTo_bob"]
            manager_card_id: str = self.employee_card_id_by_email[manager_email]

            set_employee_manager_async_tasks.append(
                self._update_cmdbuild_card(
                    data={"ReportsTo": manager_card_id},
                    card_id=employee_card_id,
                    class_id="InternalEmployee",
                )
            )
        await asyncio.gather(*set_employee_manager_async_tasks)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
