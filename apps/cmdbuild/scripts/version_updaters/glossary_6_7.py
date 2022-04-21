import pandas as pd
from logging import Logger
from typing import NoReturn, Dict, List
from scripts.web_clients.cmdbuild import CmdBuildWebClient
from scripts.web_clients.hibob import HiBobWebClient
from scripts.common.constants import PROJECT_ROOT
from typing import NoReturn, Dict, List
from scripts.components.relation import RelationComponent
from collections import defaultdict
import concurrent.futures


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


def create_relation(
    service_card_id: str, 
    employee_card_id: str, 
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
):
    cmdbuild_client.path = f"rest/v3/classes/InternalEmployee/cards/{employee_card_id}/relations"
    relation_component: RelationComponent = RelationComponent(
        domain_name="ServiceAccessService",
        destinationId=service_card_id,
        destinationType="TechnicalService",
        sourceType="InternalEmployee",
        sourceId=employee_card_id,
        is_direct="true",
        destinationDescription="",
        destinationCode=""
    )
    schema = RelationComponent.schema()
    component_dump: Dict = schema.dump(relation_component)
    cmdbuild_client.create(component_data=component_dump)
    logger.info(f"Relation between employee {service_card_id} and service {employee_card_id} is established")


def check_relations(
    card_id_by_employee: Dict,
    services_accesses_by_employee_id: Dict,
    cmdbuild_client: CmdBuildWebClient,
    domain_name: str,
):
    employee_counter = 0
    employee_by_card_id = {card_id: employee for employee, card_id in card_id_by_employee.items()}
    for employee_counter, (employee_id, exptected_accesses) in enumerate(services_accesses_by_employee_id.items()):

        cmdbuild_client.path = f"rest/v3/classes/InternalEmployee/cards/{employee_id}/relations"
        current_accesses = set()
        relations_info = cmdbuild_client.get_all()
        for relation in relations_info:
            if relation['_type'] == domain_name:
                current_accesses.add(relation['_destinationId'])

        employee_name: str = employee_by_card_id[employee_id]
        assert current_accesses == exptected_accesses, f'relations for employee {employee_name} are not complete!'
        print(f'{employee_counter} employee {employee_name} is checked!')


def establish_access_relations(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
    ) -> NoReturn:

    card_id_by_service: Dict = get_service_card_id(cmdbuild_client, logger)
    card_id_by_employee: Dict = get_employee_card_id(cmdbuild_client, logger)

    yolo_user_accesses_path: str = f'{PROJECT_ROOT}/Yolo User Accesses.xlsx'
    xls: pd.ExcelFile = pd.ExcelFile(yolo_user_accesses_path)
    yolo_user_accesses_df: pd.DataFrame = pd.read_excel(xls, "IT apps for Internal Users")

    users = yolo_user_accesses_df['Applications'].unique()
    services_accesses_by_employee_id = defaultdict(set)
    for service_name in yolo_user_accesses_df.columns:
        replaced_service_name: str = parsing_rules["service"]["replace"].get(service_name, service_name).strip()

        skip_service_fields: bool = replaced_service_name in ('Unnamed: 0', 'Unnamed: 1', 'Applications')
        service_card_is_absent_in_cmdbuild: bool = replaced_service_name not in card_id_by_service
        if skip_service_fields or service_card_is_absent_in_cmdbuild:
            continue

        accesses = yolo_user_accesses_df[service_name]
        service_card_id: str = card_id_by_service[replaced_service_name]
        for user_name, access_flag in zip(users, accesses):

            user_has_not_access: bool = access_flag != 'Yes'
            user_name_is_invalid: bool = not isinstance(user_name, str)
            access_flag_is_invalid: bool = not isinstance(access_flag, str)

            if user_has_not_access or user_name_is_invalid or access_flag_is_invalid:
                continue

            replaced_user_name: str = parsing_rules["user"]["replace"].get(user_name, user_name).strip()
            employee_card_is_absent_in_cmdbuild: bool = replaced_user_name not in card_id_by_employee
            if employee_card_is_absent_in_cmdbuild:
                continue

            employee_card_id: str = card_id_by_employee[replaced_user_name]
            services_accesses_by_employee_id[employee_card_id].add(service_card_id)

    for employee_id, services_accesses in services_accesses_by_employee_id.items():
        max_workers = len(services_accesses)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            service_id_by_future = {
                executor.submit(create_relation, service_card_id, employee_id, cmdbuild_client, logger): service_card_id 
                for service_card_id in services_accesses
            }

    check_relations(card_id_by_employee, services_accesses_by_employee_id, cmdbuild_client, 'ServiceAccessService')


