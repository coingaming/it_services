import re
import pandas as pd
from collections import defaultdict
from logging import Logger
from typing import NoReturn, Dict, List, Tuple
from scripts.web_clients.cmdbuild import CmdBuildWebClient
from scripts.web_clients.hibob import HiBobWebClient
from scripts.common.constants import YoloITServiceAttr, PROJECT_ROOT
from scripts.components.card import ServiceComponent, ServiceCategoryComponent
from scripts.components.relation import RelationComponent
from typing import NoReturn, Dict, List



parsing_rules = {
    YoloITServiceAttr.SERVICE_NAME: {
        "replace": {
            float('nan'): None,
        }
    },
    YoloITServiceAttr.CATEGORY: {
        "replace": {
            float('nan'): "Other",
            'Device management': 'Device Management',
            'Project management': 'Project Management',
            'Database tool': 'Database Tool',
            'Testing tool': 'Testing Tool',
            'Bookmaker tool': 'Bookmaker Tool',
            'Identity hub': 'Identity Hub',
            'Session recording': 'Session Recording',
            'Image processing tool': 'Image Processing Tool',
            'Marketing tool': 'Marketing Tool',
            'Reporting tool': 'Reporting Tool',
            'Development tool': 'Development Tool',
        },

        "index": {
            'Other': 'OTHER',
            'Payments': 'PAY',
            'Design Tools': 'DT',
            'Assets': 'A',
            'Grammar Tools': 'GT',
            'Device Management': 'DM',
            'Learning': 'LEARNING',
            'SEO Tool': 'SEO',
            'Project Management': 'PM',
            'Database Tool': 'DB',
            'Testing Tool': 'QA',
            'Backoffice': 'BO',
            'Bookmaker Tool': 'BM',
            'Core Infrastructure': 'CI',
            'Communication': 'CM',
            'Security': 'SC',
            'Identity Hub': 'ID',
            'Session Recording': 'SR',
            'Image Processing Tool': 'IMGP',
            'Marketing Tool': 'MT',
            'Reporting Tool': 'RT',
            'Development Tool': 'DEV',
        }
    },

    YoloITServiceAttr.OWNER: {
        "replace": {
        }
    },

    YoloITServiceAttr.ADMIN_ACCESS : {
        "replace": {
        },

    "move_to_description": {
        }
    }
}


def __cleanup_categories(
    cmdbuild_client: CmdBuildWebClient
):
    class_id: str = 'TechnicalService'
    cmdbuild_client.path = f'rest/v3/classes/{class_id}/cards'
    cards = cmdbuild_client.get_all()
    for card in cards:
        cmdbuild_client.delete(card['_id'])

    class_id: str = 'ServiceCategory'
    cmdbuild_client.path = f'rest/v3/classes/{class_id}/cards'
    cards = cmdbuild_client.get_all()
    for card in cards:
        cmdbuild_client.delete(card['_id'])


def get_OU_id(
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
) -> Dict:

    class_id: str = "OU"
    cmdbuild_client.path = f"rest/v3/classes/{class_id}/cards"
    OU: List[Dict] = cmdbuild_client.get_all()
    OU_by_card_id: Dict = {item['_id']: item['Name'] for item in OU}
    return OU_by_card_id


def get_employee_card_id(
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
) -> Tuple[Dict, Dict]:

    cmdbuild_client.path = f"rest/v3/classes/Customer/cards"
    companies: List[Dict] = cmdbuild_client.get_all()
    company_by_card_id: Dict = {company['_id']: company['CompanyTitle'] for company in companies}

    cmdbuild_client.path = f"rest/v3/classes/InternalEmployee/cards"
    employees: List[Dict] = cmdbuild_client.get_all()

    card_id_by_employee = {}
    employee_grouped_by_OU = defaultdict(list)
    for employee in employees:
        first_name, last_name = employee['FirstName'], employee['LastName']
        fullname: str = f"{first_name} {last_name}"
        card_id_by_employee[fullname] = employee['_id']
        ou: str = employee['_OU_description']
        company_id: str = employee['Company']
        company_title: str = company_by_card_id[company_id]

        append_to_group = False
        match (ou, company_title):
            case ("Fraud and Payments", _):
                append_to_group = True
            case ("Devops", _):
                append_to_group = True
            case ("Accounting", "Heathmont OÜ"):
                append_to_group = True

        if append_to_group:
            employee_grouped_by_OU[ou].append(fullname) #(first_name, last_name,))

    return (card_id_by_employee, employee_grouped_by_OU)


def create_service_category_cards(
    yolo_it_service_library: pd.DataFrame,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
) -> Dict:

    class_id: str = "ServiceCategory"
    cmdbuild_client.path = f"rest/v3/classes/{class_id}/cards"
    service_categories: List[str] = yolo_it_service_library['Category'].unique()
    category_parsing_rules: Dict = parsing_rules[YoloITServiceAttr.CATEGORY]
    cards_id_by_category: Dict = {}
    for category in service_categories:
        category_component: ServiceCategoryComponent = ServiceCategoryComponent(
            parent = None,
            code = category,
            description = category,
            state = "Active",
            index = category_parsing_rules["index"][category],
        )
        category_schema = ServiceCategoryComponent.schema()
        category_dump: Dict = category_schema.dump(category_component)
        category_id: str = cmdbuild_client.create(component_data=category_dump)
        cards_id_by_category[category] = category_id
        logger.info(f"Category {category} for class {class_id} is created")

    return cards_id_by_category


def create_service_cards(
    yolo_it_service_library: pd.DataFrame,
    cards_id_by_category: Dict,
    card_id_by_employee: Dict,
    employee_grouped_by_OU: Dict,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
):  

    regex = re.compile(r'\((.*?)\)')
    admins_access_parsing_rules: Dict = parsing_rules[YoloITServiceAttr.ADMIN_ACCESS]
    for row in yolo_it_service_library.itertuples():
        service: str = row[YoloITServiceAttr.SERVICE_NAME]
        if service is None:
            continue

        service: str = service.strip()
        owner: str = row[YoloITServiceAttr.OWNER].strip()
        admins_access: str = row[YoloITServiceAttr.ADMIN_ACCESS].strip()
        category_name: str = row[YoloITServiceAttr.CATEGORY]

        proceed_admins_access: List = []
        description: str = ""
        for item in admins_access.split(', '):
            move_to_description: bool = item in admins_access_parsing_rules["move_to_description"]
            if move_to_description:
                description = item
            else:
                admin_name_without_brackets: str = re.sub(regex, r"", item).strip()
                admin_name: str = admins_access_parsing_rules["replace"].get(admin_name_without_brackets, admin_name_without_brackets)

                if admin_name in employee_grouped_by_OU:
                    proceed_admins_access = [card_id_by_employee[name] for name in employee_grouped_by_OU.get(admin_name, ())]
                elif admin_name in card_id_by_employee:
                    proceed_admins_access.append(card_id_by_employee[admin_name])
                else:
                    print(f"missed admin_name={admin_name} for service={service}")

        service_component: ServiceComponent = ServiceComponent(
            category=cards_id_by_category[category_name],
            name=service,
            service_state="Active",
            service_owner=card_id_by_employee.get(owner),
            extended_description=description
        )

        schema = ServiceComponent.schema()
        cmdbuild_client.path = f"rest/v3/classes/TechnicalService/cards"
        component_dump: Dict = schema.dump(service_component)
        service_card_id: str = cmdbuild_client.create(component_data=component_dump)

        for admin in proceed_admins_access:
            cmdbuild_client.path = f"rest/v3/classes/InternalEmployee/cards/{admin}/relations"
            relation_component: RelationComponent = RelationComponent(
                domain_name="ServiceAdminService",
                destinationId=service_card_id,
                destinationType="TechnicalService",
                sourceType="InternalEmployee",
                sourceId=admin,
                is_direct="true",
                destinationDescription="",
                destinationCode=""
            )
            schema = RelationComponent.schema()
            component_dump: Dict = schema.dump(relation_component)
            cmdbuild_client.create(component_data=component_dump)


def cleanup(
    yolo_it_service_library: pd.DataFrame,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
):
    attributes: Tuple = (YoloITServiceAttr.SERVICE_NAME, YoloITServiceAttr.ADMIN_ACCESS, YoloITServiceAttr.OWNER, YoloITServiceAttr.CATEGORY)
    columns: Tuple = ('Service name', 'Admin Access', 'Owner', 'Category')
    for attr, column in zip(attributes, columns):
        item_parsing_rules: Dict = parsing_rules[attr]
        for _from, _to in item_parsing_rules["replace"].items():
            yolo_it_service_library[column] = yolo_it_service_library[column].replace([_from], _to)


def create_services_cards(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
    ) -> NoReturn:

    yolo_it_service_library_path: str = f'{PROJECT_ROOT}/Yolo IT Service Library.xlsx'
    xls: pd.ExcelFile = pd.ExcelFile(yolo_it_service_library_path)
    yolo_it_service_library: pd.DataFrame = pd.read_excel(xls, "IT services")

    cleanup(yolo_it_service_library, cmdbuild_client, logger)
    cards_id_by_category: Dict = create_service_category_cards(yolo_it_service_library, cmdbuild_client, logger)
    card_id_by_employee, employee_grouped_by_OU = get_employee_card_id(cmdbuild_client, logger)
    create_service_cards(yolo_it_service_library, cards_id_by_category, card_id_by_employee, employee_grouped_by_OU, cmdbuild_client, logger)
