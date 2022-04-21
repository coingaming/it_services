import pandas as pd
from typing import NoReturn, Dict, Tuple, List
from scripts.web_clients.cmdbuild import CmdBuildWebClient
from scripts.web_clients.hibob import HiBobWebClient
from scripts.components.card import EmployeeCardComponent
from scripts.components.relation import RelationComponent
from logging import Logger
from scripts.common.constants import PROJECT_ROOT
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
    employee_class: str,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
) -> Dict:

    cmdbuild_client.path = f"rest/v3/classes/{employee_class}/cards"
    employees: List[Dict] = cmdbuild_client.get_all()
    card_id_by_service: Dict = {employee['DisplayName']: employee['_id'] for employee in employees}
    return card_id_by_service


def create_external_employee_cards(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
    ) -> NoReturn:

    yolo_user_accesses_path: str = f'{PROJECT_ROOT}/Yolo User Accesses.xlsx'
    xls: pd.ExcelFile = pd.ExcelFile(yolo_user_accesses_path)
    yolo_user_accesses_df: pd.DataFrame = pd.read_excel(xls, "IT apps for External Users")

    card_id_by_service: List[Dict] = get_service_card_id(cmdbuild_client, logger)
    card_id_by_employee: List[Dict] = get_employee_card_id('InternalEmployee', cmdbuild_client, logger)

    managers: List = [manager for manager in yolo_user_accesses_df['Unnamed: 1']]
    external_employees: List = [user for user in yolo_user_accesses_df['Applications'].unique()]
    services: List = [service for service in yolo_user_accesses_df.columns if service not in {'Unnamed: 0', 'Unnamed: 130', 'Unnamed: 44', 'Applications', 'Unnamed: 1'}]

    # create external employee cards
    class_id: str = "ExternalEmployee"
    cmdbuild_client.path = f"rest/v3/classes/{class_id}/cards"
    for manager, employee in zip(managers, external_employees):
        manager_replaced: str = parsing_rules["user"]["replace"].get(str(manager), manager)
        component = EmployeeCardComponent(
            code=None,
            lastName=employee,
            firstName=None,
            displayName=employee,
            jobTitle=None,
            email=None,
            state="Active",
            type="Regular",
            reportsTo=card_id_by_employee.get(manager_replaced)
        )
        schema = EmployeeCardComponent.schema(
            only=(
                'LastName',
                'DisplayName',
                'ReportsTo',
            )
        )
        component_dump: Dict = schema.dump(component)
        card_id: int = cmdbuild_client.create(component_data=component_dump)
        card_id_by_employee[employee] = card_id
        logger.info(f"Card {employee} for class {class_id} is created")

    # gather info about accesses
    card_id_by_external_employee: List[Dict] = get_employee_card_id('ExternalEmployee', cmdbuild_client, logger)
    services_accesses_by_employee_id = defaultdict(set)
    for service_name in services:
        replaced_service_name: str = parsing_rules["service"]["replace"].get(service_name, service_name).strip()
        service_card_is_absent_in_cmdbuild: bool = replaced_service_name not in card_id_by_service
        if service_card_is_absent_in_cmdbuild:
            continue

        accesses = yolo_user_accesses_df[service_name]
        service_card_id: str = card_id_by_service[replaced_service_name]
        for employee, access_flag in zip(external_employees, accesses):

            user_has_not_access: bool = str(access_flag).lower() != 'yes'
            if user_has_not_access:
                continue

            employee_card_id: str = card_id_by_external_employee[employee]
            services_accesses_by_employee_id[employee_card_id].add(service_card_id)

    # create relations between external employees and services
    for employee_id, services_accesses in services_accesses_by_employee_id.items():
        max_workers = len(services_accesses)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            service_id_by_future = {
                executor.submit(create_relation, service_card_id, employee_id, cmdbuild_client, logger): service_card_id 
                for service_card_id in services_accesses
            }
    check_relations(card_id_by_external_employee, services_accesses_by_employee_id, cmdbuild_client, 'ServiceAccessService')


def create_relation(
    service_card_id: str, 
    employee_card_id: str, 
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
):
    cmdbuild_client.path = f"rest/v3/classes/ExternalEmployee/cards/{employee_card_id}/relations"
    relation_component: RelationComponent = RelationComponent(
        domain_name="ServiceAccessService",
        destinationId=service_card_id,
        destinationType="TechnicalService",
        sourceType="ExternalEmployee",
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
    for employee_counter, (employee_id, expected_accesses) in enumerate(services_accesses_by_employee_id.items()):

        cmdbuild_client.path = f"rest/v3/classes/ExternalEmployee/cards/{employee_id}/relations"
        current_accesses = set()
        relations_info = cmdbuild_client.get_all()
        for relation in relations_info:
            if relation['_type'] == domain_name:
                current_accesses.add(relation['_destinationId'])

        employee_name: str = employee_by_card_id[employee_id]
        assert current_accesses == expected_accesses, f'relations for employee {employee_name} are not complete! current={current_accesses} expected={expected_accesses}'
        print(f'{employee_counter} employee {employee_name} is checked!')