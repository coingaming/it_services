from enum import IntEnum, auto
import pandas as pd
from logging import Logger
from typing import NoReturn, Dict, List
from scripts.web_clients.cmdbuild import CmdBuildWebClient
from scripts.web_clients.hibob import HiBobWebClient
from scripts.components.card import OUComponent, EmployeeCardComponent, CompanyComponent


class EMPLOYEE_FRAME_COLUMNS(IntEnum):
    CODE = 1
    FIRST_NAME = auto()
    SURNAME = auto()
    DISPLAY_NAME = auto()
    EMAIL = auto()
    IS_MANAGER = auto()
    REPORT_TO = auto()
    TITLE = auto()
    DEPARTMENT = auto()
    SERVICE_OWNER = auto()
    COMPANY = auto()


def __cleanup_department_cards(
    cmdbuild_client: CmdBuildWebClient
):
    class_id: str = 'OU'
    cmdbuild_client.path = f'rest/v3/classes/{class_id}/cards'
    cards = cmdbuild_client.get_all()
    for card in cards:
        cmdbuild_client.delete(card['_id'])
    class_id: str = 'Customer'
    cmdbuild_client.path = f'rest/v3/classes/{class_id}/cards'
    cards = cmdbuild_client.get_all()
    for card in cards:
        cmdbuild_client.delete(card['_id'])


def __cleanup_employee_cards(
    cmdbuild_client: CmdBuildWebClient
):

    class_id: str = 'InternalEmployee'
    cmdbuild_client.path = f'rest/v3/classes/{class_id}/cards'
    cards = cmdbuild_client.get_all()

    employees = [card['_id'] for card in cards if not card['IsManager']]
    managers = [card['_id'] for card in cards if card['IsManager']]
    for card in employees:
        cmdbuild_client.delete(card)
    for card in managers:
        try:
            cmdbuild_client.delete(card)
        except Exception:
            pass

def clear_all(cmdbuild_client):
    __cleanup_employee_cards(cmdbuild_client)
    __cleanup_department_cards(cmdbuild_client)


def create_cards(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
    ) -> NoReturn:

    #clear_all(cmdbuild_client)
    employee_df: pd.DataFrame = __pull_employees(hibob_client, logger)
    cards_id_by_company: Dict = __create_company_cards(employee_df, cmdbuild_client, logger)
    cards_id_by_department: Dict = __create_department_cards(cards_id_by_company, employee_df, cmdbuild_client, logger)
    __create_employee_cards(cards_id_by_department, cards_id_by_company, employee_df, cmdbuild_client, logger)


def __create_company_cards(
    employee_df: pd.DataFrame,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
    ) -> Dict:

    class_id: str = "Customer" # todo Company
    cmdbuild_client.path = f"rest/v3/classes/{class_id}/cards"
    companies: List = employee_df[EMPLOYEE_FRAME_COLUMNS.COMPANY].unique()
    cards_id_by_company: Dict = {}
    for company in companies:
        company_component: CompanyComponent = CompanyComponent(companyTitle = company or "null")
        schema = CompanyComponent.schema(only=("CompanyTitle",))
        component_dump: Dict = schema.dump(company_component)
        component_id = cmdbuild_client.create(component_data=component_dump)
        cards_id_by_company[company] = component_id
        logger.info(f"Card {company} for class {class_id} is created")
    return cards_id_by_company


def __pull_employees(
    hibob_client: HiBobWebClient,
    logger: Logger
    ) -> pd.DataFrame:

    payload: Dict = hibob_client.pull(stream=False)
    employee_df: pd.DataFrame = pd.DataFrame(
        columns=[e.value for e in EMPLOYEE_FRAME_COLUMNS]
    )
    for row_idx, item in enumerate(payload['employees']):
        match item:
            case {
                'work': {'manager': manager_code},
                'humanReadable': {
                    'work': work,
                    'id': code,
                    'surname': surname,
                    'firstName': first_name,
                    'email': email,
                    'displayName': display_name,
                }
            }:

                department: str = work['department']
                is_manager: bool = work['isManager']
                title: str = work['title']
                company: str = work.get('customColumns', {}).get('column_1620839439167', None)

                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.CODE] = code
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.DISPLAY_NAME] = display_name
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.FIRST_NAME] = first_name
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.SURNAME] = surname
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.EMAIL] = email
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.IS_MANAGER] = is_manager
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.REPORT_TO] = manager_code
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.TITLE] = title
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.DEPARTMENT] = department
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.COMPANY] = company
    return employee_df


def __create_department_cards(
    cards_id_by_company: Dict,
    employee_df: pd.DataFrame,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
    ) -> Dict:

    class_id: str = "OU"
    cmdbuild_client.path = f"rest/v3/classes/{class_id}/cards"
    cards_id_by_department: Dict = {}
    df = employee_df.groupby(by=[EMPLOYEE_FRAME_COLUMNS.COMPANY, EMPLOYEE_FRAME_COLUMNS.DEPARTMENT],  as_index=False).first()
    for row in df.itertuples():
        company: str = row[1]
        department: str = row[2]
        company_card_id: int = cards_id_by_company[company]
        ou_component: OUComponent = OUComponent(
            name = department,
            description = department,
            company = company_card_id
        )
        schema = OUComponent.schema(only=("Name", "Company"))
        component_dump: Dict = schema.dump(ou_component)
        component_id = cmdbuild_client.create(component_data=component_dump)
        cards_id_by_department[department] = component_id
        logger.info(f"Card {department} for class {class_id} is created")
    return cards_id_by_department


def __create_employee_cards(
    cards_id_by_department: Dict,
    cards_id_by_company: Dict,
    employee_df: pd.DataFrame,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
    ):

    class_id: str = "InternalEmployee"
    cmdbuild_client.path = f"rest/v3/classes/{class_id}/cards"
    card_id_by_employee_code: Dict = {}
    # first pass: create employee cards
    for row in employee_df.itertuples():
        code: str = row[EMPLOYEE_FRAME_COLUMNS.CODE]
        last_name: str = row[EMPLOYEE_FRAME_COLUMNS.SURNAME]
        first_name: str = row[EMPLOYEE_FRAME_COLUMNS.FIRST_NAME]
        display_name: str = row[EMPLOYEE_FRAME_COLUMNS.DISPLAY_NAME]
        title: str = row[EMPLOYEE_FRAME_COLUMNS.TITLE]
        email: str = row[EMPLOYEE_FRAME_COLUMNS.EMAIL]
        is_manager: bool = row[EMPLOYEE_FRAME_COLUMNS.IS_MANAGER]
        manager_code: str = row[EMPLOYEE_FRAME_COLUMNS.REPORT_TO]
        OU_name: str = row[EMPLOYEE_FRAME_COLUMNS.DEPARTMENT]
        company: str = row[EMPLOYEE_FRAME_COLUMNS.COMPANY]
        company_id: str = cards_id_by_company[company]
        OU_id: str = cards_id_by_department[OU_name]
        component = EmployeeCardComponent(
            code=code,
            lastName=last_name,
            firstName=first_name,
            displayName=display_name,
            jobTitle=title,
            email=email,
            state="Active",
            type="Regular",
            OU=OU_id,
            isManager = is_manager == "Yes",
            company=company_id
        )

        schema = EmployeeCardComponent.schema(
            only=(
                "Code",
                'FirstName',
                'LastName',
                'DisplayName',
                'JobTitle',
                'Email',
                'State',
                'Type',
                'OU',
                'IsManager',
                'Company',
                )
            )

        component_dump: Dict = schema.dump(component)
        card_id: int = cmdbuild_client.create(component_data=component_dump)
        card_id_by_employee_code[code] = card_id
        logger.info(f"Card {first_name} {last_name} for class {class_id} is created")

    # second pass: establish employee-manager relations
    for row in employee_df.itertuples():
        last_name: str = row[EMPLOYEE_FRAME_COLUMNS.SURNAME]
        first_name: str = row[EMPLOYEE_FRAME_COLUMNS.FIRST_NAME]
        code: str = row[EMPLOYEE_FRAME_COLUMNS.CODE]
        manager_code: str = row[EMPLOYEE_FRAME_COLUMNS.REPORT_TO]
        employee_card_id: str = card_id_by_employee_code[code]
        manager_card_id: str = card_id_by_employee_code.get(manager_code)
        if manager_card_id is None:
            logger.warning(f'Employee {first_name} {last_name} does not have direct manager')
            continue

        component = EmployeeCardComponent(
            code=None,
            lastName=None,
            firstName=None,
            email=None,
            displayName=None,
            jobTitle=None,
            state=None,
            type=None,
            reportsTo=manager_card_id
        )
        schema = EmployeeCardComponent.schema(only=("ReportsTo",))
        cmdbuild_client.update(
            component_id=employee_card_id,
            component_data=schema.dump(component)
        )
        logger.info(f"Manager for {first_name} {last_name} is set")