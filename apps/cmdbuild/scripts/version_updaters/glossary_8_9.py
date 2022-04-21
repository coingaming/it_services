import pandas as pd
from typing import NoReturn, Dict, Tuple, List
from scripts.web_clients.cmdbuild import CmdBuildWebClient
from scripts.web_clients.hibob import HiBobWebClient
from scripts.components.card import ServiceComponent
from logging import Logger
from scripts.common.constants import PROJECT_ROOT


parsing_rules = {
    "user": {
        "replace": {
        }
    },
    "service": {
        "replace": {
        }
    }
}


def get_service_card_id(
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
) -> Dict:

    cmdbuild_client.path = f"rest/v3/classes/TechnicalService/cards"
    services: List[Dict] = cmdbuild_client.get_all()
    card_id_by_service: Dict = {service['Name'].strip(): service['_id'] for service in services}
    return card_id_by_service


def get_employee_card_id(
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
) -> Dict:

    cmdbuild_client.path = f"rest/v3/classes/InternalEmployee/cards"
    employees: List[Dict] = cmdbuild_client.get_all()
    card_id_by_service: Dict = {f"{employee['FirstName']} {employee['LastName']}": employee['_id'] for employee in employees}
    return card_id_by_service


def create_master_admins_cards(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
    ) -> NoReturn:

    yolo_user_accesses_path: str = f'{PROJECT_ROOT}/Yolo User Accesses.xlsx'
    xls: pd.ExcelFile = pd.ExcelFile(yolo_user_accesses_path)
    yolo_user_accesses_df: pd.DataFrame = pd.read_excel(xls, "IT apps for Internal Users")
    services_info: Tuple = next(yolo_user_accesses_df.iterrows())

    card_id_by_service: Dict = get_service_card_id(cmdbuild_client, logger)
    card_id_by_employee: Dict = get_employee_card_id(cmdbuild_client, logger)

    service_by_admin: pd.Series
    _, service_by_admin = services_info
    cmdbuild_client.path = f"rest/v3/classes/TechnicalService/cards"
    for service, admin in service_by_admin.items():
        replaced_service_name: str = parsing_rules["service"]["replace"].get(service, service).strip()

        service_is_missed: bool = replaced_service_name not in card_id_by_service
        user_name_is_invalid: bool = not isinstance(admin, str)
        if user_name_is_invalid or service_is_missed:
            continue

        replaced_user_name: str = parsing_rules["user"]["replace"].get(admin, admin)
        component = ServiceComponent(
            category=None,
            name=None,
            service_state=None,
            service_owner=None,
            serviceMasterAdmin=card_id_by_employee.get(replaced_user_name),
            extended_description=None
        )
        schema = ServiceComponent.schema(only=("ServiceMasterAdmin",))
        cmdbuild_client.update(
            component_id=card_id_by_service[replaced_service_name],
            component_data=schema.dump(component)
        )
        logger.info(f"Attribute ServiceMasterAdmin is added to service {replaced_service_name}")