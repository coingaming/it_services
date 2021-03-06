import asyncio
import os
import base64
import hmac
import hashlib
import ssl
from urllib.parse import urlparse
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, fields
from pathlib import Path, PosixPath
import yaml
import httpx
import pandas as pd


PROJECT_ROOT: PosixPath = Path(__file__).parent.parent


def get_base_url(config: Dict, system) -> Dict:
    sys_config: Dict = config[system]
    if config["debug"]:
        return sys_config["url"]["debug"]
    return sys_config["url"]["prod"]


def prepate_ssl_context(url: str) -> ssl.SSLContext:
    parsed_url = urlparse(url)
    port: int = int(parsed_url.port or 443)
    cert: str = ssl.get_server_certificate(addr=(parsed_url.hostname, port))
    context = ssl.SSLContext()
    context.load_verify_locations(cadata=cert)
    return context


def filter_equal(attr, value) -> str:
    """ """
    return {
        "attribute":{
            "simple":{
                "attribute":attr,
                "operator":"equal",
                "value":[value]
            }
        }
    }


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


def generate_signature(payload: bytes) -> str:
    webhook_secret: str = read_env_variable("BOB_SECRET_KEY")
    digest = hmac.new(webhook_secret.encode("utf-8"), payload, hashlib.sha512).digest()
    calculated_signature: str = base64.b64encode(digest).decode()
    return calculated_signature


def verify_signature(received_signature: str, payload: bytes) -> bool:
    """
    Helper-function to verify reqiest signature from hibob
    """
    return hmac.compare_digest(generate_signature(payload), received_signature)


@dataclass(init=True)
class Employee:
    first_name: str
    middle_name: str
    last_name: str
    display_name: str
    full_name: str
    is_manager: bool
    email: str
    job_title: str
    email_reports_to: str  # email of employee`s manager (used as unique ID)
    o_u_title: str  # department name in HiBob
    company_title: str  # company name in HiBob
    company: int  # # REF to company card in cmdbild
    o_u: int  # REF to department card in cmdbild
    reports_to: int  # REF to manager card inOU_title_bob cmdbild
    code: str  # employee ID identifier in HiBob
    card_id: int  # employee ID identifier in Cmdbuild
    state: str

    def __init__(self, **kwargs):
        [setattr(self, fld.name, kwargs.get(fld.name)) for fld in fields(self)]

    @classmethod
    def create_from_cmdb_dump(cls, employee_payload: Dict) -> "Employee":
        pass  # TODO

    @classmethod
    def create_from_bob_dump(cls, employee_payload: Dict) -> "Employee":
        match employee_payload:
            case {
                "internal": internal,
                "work": {
                    "reportsTo": reports_to,
                },
                "humanReadable": human_readable,
            }:
                # mandatory fields
                status: str = internal["status"]
                bob_id: str = human_readable["id"]  # PK generated by hibob
                work_info: Dict = human_readable["work"]
                # optional fields
                department: str = work_info.get("department")
                is_manager: bool = work_info.get("isManager") == "Yes"
                job_title: str = work_info.get("title")
                company_title: str = work_info.get("customColumns", {}).get(
                    EmployeeInterSystemsContext.bob_custom_company_column_id
                )
                email_reports_to = (
                    None if reports_to is None else reports_to["email"]
                )  # top management may not have reports to field
                bob_id: str = human_readable["id"]  # PK generated by hibob
                first_name: str = human_readable.get("firstName")
                middle_name: str = human_readable.get("middleName")
                last_name: str = human_readable.get("surname")
                display_name: str = human_readable.get("displayName")
                full_name: str = human_readable.get("fullName")
                email: str = human_readable.get("email")
                return cls(
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    display_name=display_name,
                    full_name=full_name,
                    is_manager=is_manager,
                    email=email,
                    email_reports_to=email_reports_to,
                    job_title=job_title,
                    o_u_title=department,
                    company_title=company_title,
                    code=bob_id,
                    state=(status if status == "Active" else "Suspended"),
                )

    def prepare_cmdb_dump(self, exclude_fields: None | List = None) -> Dict:
        # assert self.reports_to is not None, "ReportTo field should be Integer (Ref type in CMDB)"
        # assert self.o_u is not None, "o_u field should be Integer (Ref type in CMDB)"
        # assert self.company is not None, "ReportTo field should be Integer (Ref type in CMDB)"
        def to_camel_case(snake_case_field: str) -> str:
            temp = snake_case_field.split("_")
            return temp[0].title() + "".join(ele.title() for ele in temp[1:])

        dump: Dict = {}
        for field in fields(self):
            attr_name: str = field.name
            attr_value = getattr(self, attr_name)
            should_exclude_field: bool = (
                exclude_fields is not None and attr_name in exclude_fields
            )
            if should_exclude_field or attr_value is None:
                continue
            dump[to_camel_case(attr_name)] = attr_value
        return dump


class EmployeeInterSystemsContext:
    """
    Reduces information about employees to a common denominator between 2 systems:
    hr and cmdbuild.
    We believe that the most relevant data is in the hr system.
    Public API 'prepare' fetches data from hr system and propogate all the changes to cmdbuild.
    """

    bob_custom_company_column_id: str = "column_1644933593840"  # "column_1620839439167"
    cmdbuild_compatible_nan: str = "nan"

    def __init__(self, bob_http_client, cmdbuild_http_client, logger):

        self.bob_client: httpx.AsyncClient = bob_http_client
        self.cmdbuild_client: httpx.AsyncClient = cmdbuild_http_client
        self.logger = logger
        self.bob_auth_header: Dict = {
            "Accept": "application/json",
            "Authorization": read_env_variable("BOB_TOKEN"),
        }
        self.cmdb_auth_header: Dict = {
            "username": read_env_variable("USER_CMDB"),
            "password": read_env_variable("PASS_CMDB"),
        }

        # local caches
        self.employee_card_id_by_email: Dict = {}
        self.employee_email_by_card_id: Dict = {}
        self.company_name_by_card_id: Dict = {}
        self.company_card_id_by_name: Dict = {}
        self.department_card_id_by_name: Dict = {}
        self.department_name_by_card_id: Dict = {}
        self.lock_cmdbuild_token = asyncio.Lock()
        self._cmdbuild_token: str = None

    #########################################################################################
    #                                   PUBLIC API                                          #
    #########################################################################################

    def clear(self):
        self.bob_client = None
        self.cmdbuild_client = None
        self.logger = None

    async def prepare(self):
        """
        The main API method.
        Fetches data from both hr system and cmdbuild.
        Based on the fact that hr system contains actual information
        Propogates it to cmdbuild
        """
        employee_fetch_result: List[Dict] = await asyncio.gather(
            self._get_all_bob_employees(),
            self._get_all_cmdb_employees_from_cmdb(),
        )
        bob_sfx: str = "_bob"
        cmdbuild_sfx: str = "_cmdbuild"
        prepared_employees_df: pd.DataFrame = self._prepare_employees_info_dataframe(
            *employee_fetch_result, suffixes=(bob_sfx, cmdbuild_sfx)
        )
        await asyncio.gather(
            self._create_departments_cards(
                departments=prepared_employees_df["o_u_title_bob"].unique()
            ),
            self._create_company_cards(
                companies=prepared_employees_df["company_title_bob"].unique()
            ),
        )
        await asyncio.gather(
            self._create_employee_card(
                employees_df=prepared_employees_df.query(
                    f"card_id_cmdbuild == '{EmployeeInterSystemsContext.cmdbuild_compatible_nan}'"
                ),
                suffixes=(bob_sfx, cmdbuild_sfx),
            ),
            self._update_employee_card(
                employees_df=prepared_employees_df.query(
                    f"card_id_cmdbuild != '{EmployeeInterSystemsContext.cmdbuild_compatible_nan}'"
                ),
                suffixes=(bob_sfx, cmdbuild_sfx),
            ),
        )

    async def create_cmdb_employee(self, employee_id: str):
        bob_employee_info: Dict = await self._get_bob_employee_by_id(employee_id)
        employee = Employee.create_from_bob_dump(bob_employee_info)
        self.logger.info('[create_cmdb_employee] new employee payload: %s', employee)
        cmdb_card_id: int | None = await self._get_cmdb_card_id_by_attr(
            class_id="InternalEmployee", filter_attr="Email", attr=employee.email
        )
        department: str = employee.o_u_title
        company: str = employee.company_title
        manager_email: str = employee.email_reports_to
        # replace company title with cmdb card id
        if company is not None:
            employee.company = await self._get_cmdb_card_id_by_attr(
                class_id="Customer",
                filter_attr="CompanyTitle",
                attr=company,
                data={"Description": company, "CompanyTitle": company},
                create_if_absent=True,
            )
        # replace organization unit name with cmdb card id
        if department is not None:
            employee.o_u = await self._get_cmdb_card_id_by_attr(
                class_id="OU",
                filter_attr="Name",
                attr=department,
                data={"Name": department, "Description": department},
                create_if_absent=True,
            )
        # replace employee`s manager with cmdb card id
        if manager_email is not None:
            employee.reports_to = await self._get_cmdb_card_id_by_attr(
                class_id="InternalEmployee", filter_attr="Email", attr=manager_email
            )
        # create new employee card in cmdbuild
        employee_dump: Dict = employee.prepare_cmdb_dump(
            exclude_fields=["email_reports_to", "o_u_title", "company_title", "card_id"]
        )
        is_employee_created_manually: bool = cmdb_card_id is not None
        self.logger.info('[create_cmdb_employee] add new employee dump: %s', employee_dump)
        if is_employee_created_manually:
            await self._update_cmdb_card(
                class_id="InternalEmployee",
                data=employee_dump,
                card_id=cmdb_card_id,
            )
        else:
            await self._create_cmdb_card(
                class_id="InternalEmployee",
                data=employee_dump
            )

    async def update_cmdb_employee(self, employee_id, update_info: Dict):
        # TODO add rate limit
        bob_employee_info: Dict = await self._get_bob_employee_by_id(employee_id)
        employee = Employee.create_from_bob_dump(bob_employee_info)
        company_path_to_match: str = (
            f"/work/customColumns/{self.bob_custom_company_column_id}"
        )
        for item_change in update_info:
            match item_change:
                case {"path": "/work/department", "newValue": department_name}:
                    department_card_id: str = await self._get_cmdb_card_id_by_attr(
                        class_id="OU",
                        filter_attr="Name",
                        attr=department_name,
                        data={"Name": department_name, "Description": department_name},
                        create_if_absent=True,
                    )
                    employee.o_u = department_card_id
                case {"path": company_path_to_match, "newValue": company_title}:
                    company_card_id: str = (
                        await self._get_cmdb_card_id_by_attr(
                            class_id="Customer",
                            filter_attr="CompanyTitle",
                            attr=company_title,
                            data={
                                "Description": company_title,
                                "CompanyTitle": company_title,
                            },
                            create_if_absent=True,
                        ),
                    )
                    employee.company = company_card_id
                case {"path": "/work/reportsTo", "newValue": {"id": manager_code}}:
                    manager_card_id = (
                        await self._get_cmdb_card_id_by_attr(
                            class_id="InternalEmployee",
                            filter_attr="Code",
                            attr=manager_code,
                        ),
                    )
                    employee.reports_to = manager_card_id
        employee_card_id = await self._get_cmdb_card_id_by_attr(
            class_id="InternalEmployee",
            filter_attr="Code",
            attr=update_info["employee"]["id"],
        )
        await self._update_cmdb_card(
            class_id="InternalEmployee",
            data=employee.asdict(),
            card_id=employee_card_id,
        )

    #########################################################################################
    #                                   PRIVATE API                                         #
    #########################################################################################

    async def _get_cmdb_card_id_by_attr(
        self,
        class_id: str,
        filter_attr: str,
        attr: str,
        data: Dict | None = None,
        create_if_absent: bool = False,
    ):
        token = await self._get_cmdbuild_token()
        card_payload_req = self.cmdbuild_client.build_request(
            method="GET",
            url=f"rest/v3/classes/{class_id}/cards",
            params={"filter": filter_equal(filter_attr, attr)},
            headers={"Cmdbuild-authorization": token},
        )
        response: httpx.Response = await self.cmdbuild_client.send(card_payload_req)
        response.raise_for_status()
        card_payload: Dict = response.json()
        data: List = card_payload["data"]
        card_id: str | None = None
        if data:
            card_id: str = data[0]['_id']
        elif create_if_absent:
            new_card_payload: Dict = await self._create_cmdb_card(
                class_id=class_id, data=data
            )
            card_id = new_card_payload["data"]["_id"]
        else:
            self.logger.warning(
                "Card for class %s and attribute %s:%s is not found",
                class_id,
                filter_attr,
                attr,
            )
        return card_id

    async def _get_cmdbuild_token(self):
        """
        Generates authentication token
        Which should be added in the header of the request
        https://www.cmdbuild.org/file/manuali/webservice-manual-in-english, Page 11
        """
        async with self.lock_cmdbuild_token:
            if self._cmdbuild_token is None:
                path: str = "rest/v3/sessions"
                req: httpx.Request = self.cmdbuild_client.build_request(
                    method="POST",
                    url=path,
                    params={"scope": "service", "returnId": True},
                    json=self.cmdb_auth_header,
                )
                response: httpx.Response = await self.cmdbuild_client.send(req)
                response.raise_for_status()
                response_payload: Dict = response.json()
                token: str = response_payload["data"]["_id"]
                self._cmdbuild_token = token
            return self._cmdbuild_token

    def _prepare_employees_info_dataframe(
        self,
        bob_employees_df: pd.DataFrame,
        cmdbuild_employees_df: pd.DataFrame,
        suffixes: Tuple[str],
    ) -> pd.DataFrame:
        """
        Combines information from hr system and cmdbuild to easily manipulate
        """
        bob_sfx, _cmdbuild_sfx = suffixes
        column_name_for_join: str = "email"
        prepared_employees_df: pd.DataFrame = pd.merge(
            bob_employees_df,
            cmdbuild_employees_df,
            on=column_name_for_join,
            how="left",
            suffixes=suffixes,
        )
        prepared_employees_df.fillna(
            value=EmployeeInterSystemsContext.cmdbuild_compatible_nan, inplace=True
        )
        prepared_employees_df.rename(
            columns={column_name_for_join: f"{column_name_for_join}{bob_sfx}"},
            inplace=True,
        )
        return prepared_employees_df

    async def _get_all_cmdb_employees_from_cmdb(self) -> pd.DataFrame:
        """
        Fetches ALL employee information from cmdbuild
        """
        requested_cards_types: Tuple[str] = ("Customer", "OU", "InternalEmployee")
        token = await self._get_cmdbuild_token()
        async_tasks: List[Dict] = [
            # send a request
            self.cmdbuild_client.send(
                # build GET request to cmdb service
                self.cmdbuild_client.build_request(
                    method="GET",
                    url=f"rest/v3/classes/{cardId}/cards",
                    headers={"Cmdbuild-authorization": token},
                )
            )
            for cardId in requested_cards_types
        ]
        results: List[httpx.Response] = await asyncio.gather(*async_tasks)
        # raise HTTPStatusError
        [resp.raise_for_status() for resp in results]
        # retrive json payload from responses
        resp_payloads: List[Dict] = [resp.json() for resp in results]
        companies_info, organization_units_info, employees_info = resp_payloads
        # update local caches
        # 1. employee local cache
        for card in employees_info["data"]:
            card_id: str = card["_id"]
            email: str = card["Email"]
            self.employee_card_id_by_email[email] = card_id
            self.employee_email_by_card_id[card_id] = email
        # 2. OU local cache
        for card in organization_units_info["data"]:
            card_id: str = card["_id"]
            name: str = card["Name"]
            self.department_card_id_by_name[name] = card_id
            self.department_name_by_card_id[card_id] = name
        # 3. Companies local cache
        for card in companies_info["data"]:
            card_id: str = card["_id"]
            descr: str = card["Description"]
            self.company_name_by_card_id[card_id] = descr
            self.company_card_id_by_name[descr] = card_id
        # prepare employee dataframe
        cmdbuild_employees: List = []
        for employee in employees_info["data"]:
            # mandatory fields
            card_id = employee["_id"]
            first_name = employee["FirstName"]
            is_manager = employee["IsManager"]
            # optional fields
            code = employee.get("Code")
            middle_name = employee.get("MiddleName")
            last_name = employee.get("LastName")
            display_name = employee.get("DisplayName")
            full_name = employee.get("FullName")
            email = employee.get("Email")
            manager_card_id = employee.get("ReportsTo")
            job_title = employee.get("JobTitle")
            department_card_id = employee.get("OU")
            company_card_id = employee.get("Company")

            email_reports_to=self.employee_email_by_card_id.get(manager_card_id)
            o_u_title=self.employee_email_by_card_id.get(department_card_id)
            company_title=self.employee_email_by_card_id.get(company_card_id)
            cmdbuild_employees.append(
                Employee(
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    display_name=display_name,
                    full_name=full_name,
                    is_manager=is_manager,
                    email=email,
                    job_title=job_title,
                    email_reports_to=email_reports_to,
                    o_u_title=o_u_title,
                    company_title=company_title,
                    code=code,
                    card_id=card_id,
                )
            )
        if not cmdbuild_employees:
            return pd.DataFrame(columns=[field.name for field in fields(Employee)])
        return pd.DataFrame(cmdbuild_employees)

    async def _get_all_bob_employees(self) -> pd.DataFrame:
        """
        Method fetches ALL employee information from HR system (hibob)
        """
        req: httpx.Request = self.bob_client.build_request(
            method="GET",
            url="people",
            params={"showInactive": False, "includeHumanReadable": True},
            headers=self.bob_auth_header,
        )
        response: httpx.Response = await self.bob_client.send(req)
        response.raise_for_status()
        bob_payload: Dict = response.json()
        bob_employees: List = [
            Employee.create_from_bob_dump(employee)
            for employee in bob_payload["employees"]
        ]
        return pd.DataFrame(bob_employees)

    async def _get_bob_employee_by_id(self, employee_id: str) -> Dict:
        req: httpx.Request = self.bob_client.build_request(
            method="GET",
            url=f"people/{employee_id}",
            params={"includeHumanReadable": True},
            headers=self.bob_auth_header,
        )
        response: httpx.Response = await self.bob_client.send(req)
        response.raise_for_status()
        return response.json()

    async def _update_cmdb_card(self, data: Dict, card_id: str, class_id: str) -> int:
        """
        Helper method which does HTTP PUT to update existing card in cmdbuild
        """
        path: str = f"rest/v3/classes/{class_id}/cards/{card_id}"
        token: str = await self._get_cmdbuild_token()
        request: httpx.Request = self.cmdbuild_client.build_request(
            method="PUT",
            url=path,
            json=data,
            headers={"Cmdbuild-authorization": token}
        )
        response: httpx.Response = await self.cmdbuild_client.send(request)
        response.raise_for_status()
        response_payload: Dict = response.json()
        assert response_payload["success"]
        self.logger.info("Cmdb card id %s with new data %s is updated", card_id, data)
        return response_payload

    async def _create_cmdb_card(self, class_id: str, data: str) -> Dict:
        """
        Helper method which does HTTP PUSH to create new card in cmdbuild
        """
        path: str = f"rest/v3/classes/{class_id}/cards"
        token: str = await self._get_cmdbuild_token()
        request: httpx.Request = self.cmdbuild_client.build_request(
            method="POST",
            url=path,
            json=data,
            headers={"Cmdbuild-authorization": token},
        )
        response: httpx.Response = await self.cmdbuild_client.send(request)
        response.raise_for_status()
        response_payload: Dict = response.json()
        assert response_payload["success"]
        self.logger.info("Cmdb card for class %s with data %s is created", class_id, data)
        return response_payload

    async def _create_company_cards(self, companies: List):
        """
        Creates new companies (Customer) cards in CMDBuild and update related caches
        """
        async_tasks: List = []
        for company in companies:
            if (
                company != EmployeeInterSystemsContext.cmdbuild_compatible_nan
                and company not in self.company_card_id_by_name
            ):
                async_tasks.append(
                    self._create_cmdb_card(
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
                department != EmployeeInterSystemsContext.cmdbuild_compatible_nan
                and department not in self.department_card_id_by_name
            ):
                async_tasks.append(
                    self._create_cmdb_card(
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
        async_tasks: List = []
        for row in employees_df.itertuples():
            employee_attrs: Dict = {}
            employee_email: str = getattr(row, f"email{bob_sfx}")
            employee_card_id: str = self.employee_card_id_by_email[employee_email]

            for field in fields(Employee):
                field_name: str = field.name
                bob_attr: str = f"{field_name}{bob_sfx}"
                cmdb_attr: str = f"{field_name}{cmdbuild_sfx}"
                bob_value: str = getattr(row, bob_attr, None)
                cmdbuild_value: str = getattr(row, cmdb_attr, None)
                if (
                    bob_value != EmployeeInterSystemsContext.cmdbuild_compatible_nan
                    and bob_value != cmdbuild_value
                ):
                    match field_name:
                        case "email_reports_to":
                            employee_attrs[
                                "reports_to"
                            ] = self.employee_card_id_by_email[bob_value]
                        case "o_u_title":
                            employee_attrs["OU"] = self.department_card_id_by_name[
                                bob_value
                            ]
                        case "company_title":
                            employee_attrs["company"] = self.company_card_id_by_name[
                                bob_value
                            ]
                        case _:
                            employee_attrs[field_name] = bob_value
            if employee_attrs:
                employee = Employee(**employee_attrs)
                dump = employee.prepare_cmdb_dump(
                    exclude_fields=[
                        "email_reports_to",
                        "o_u_title",
                        "company_title",
                        "card_id",
                    ]
                )
                async_tasks.append(
                    self._update_cmdb_card(
                        data=dump,
                        card_id=employee_card_id,
                        class_id="InternalEmployee",
                    )
                )
        await asyncio.gather(*async_tasks)

    async def _create_employee_card(
        self, employees_df: pd.DataFrame, suffixes: Tuple[str]
    ) -> int:
        """
        Creates new cmdbuild card for InternalEmployee class
        """
        bob_sfx, _ = suffixes
        create_employees_async_tasks: List = []
        for row in employees_df.itertuples():

            employee_attrs: Dict = {}
            for field in fields(Employee):
                attr_name: str = field.name
                value = getattr(row, f"{attr_name}{bob_sfx}")
                if value != self.cmdbuild_compatible_nan:
                    employee_attrs[attr_name] = value

            employee = Employee(**employee_attrs)
            # replace organization unit name with card id in cmdb
            if employee.o_u_title is not None:
                employee.o_u = self.department_card_id_by_name[employee.o_u_title]
            # replace company title with card id in cmdb
            if employee.company_title is not None:
                employee.company = self.company_card_id_by_name[employee.company_title]

            dump: Dict = employee.prepare_cmdb_dump(
                exclude_fields=[
                    "email_reports_to",
                    "o_u_title",
                    "company_title",
                    "card_id",
                    "reports_to"
                ]
            )
            create_employees_async_tasks.append(
                self._create_cmdb_card(
                    class_id="InternalEmployee",
                    data=dump,
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
            # employee may not has a manager
            manager_email: str = getattr(row, "email_reports_to_bob")
            if manager_email != self.cmdbuild_compatible_nan:
                manager_card_id: str = self.employee_card_id_by_email[manager_email]
                employee_email: str = getattr(row, "email_bob")
                employee_card_id: str = self.employee_card_id_by_email[employee_email]
                set_employee_manager_async_tasks.append(
                    self._update_cmdb_card(
                        data={"ReportsTo": manager_card_id},
                        card_id=employee_card_id,
                        class_id="InternalEmployee",
                    )
                )
        await asyncio.gather(*set_employee_manager_async_tasks)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
