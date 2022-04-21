from scripts.components.card import CompanyComponent, EmployeeCardComponent
from typing import NoReturn, Dict, Tuple, List
from scripts.web_clients.cmdbuild import CmdBuildWebClient
from scripts.web_clients.hibob import HiBobWebClient
from logging import Logger


def create_edufy_cards(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
    ) -> NoReturn:

    company_name: str = 'Edify Marketing'
    cmdbuild_client.path = f"rest/v3/classes/Customer/cards"
    company_component: CompanyComponent = CompanyComponent(companyTitle = company_name)
    schema = CompanyComponent.schema(only=("CompanyTitle",))
    component_dump: Dict = schema.dump(company_component)
    company_card_id = cmdbuild_client.create(component_data=component_dump)

    reports_to_default: str = 'Priyank Shah'
    edify_marketing: Tuple[Dict] = (
    )

    cmdbuild_client.path = f"rest/v3/classes/InternalEmployee/cards"
    employees: List[Dict] = cmdbuild_client.get_all()
    card_id_by_employee = {f"{employee['FirstName']} {employee['LastName']}": employee['_id'] for employee in employees}
    for employee_info in edify_marketing:
        first_name: str = employee_info['first_name']
        last_name: str = employee_info['last_name']
        employee_full_name: str = f"{first_name} {last_name}"
        email: str = employee_info['email']
        is_manager: bool = employee_info.get('is_manager')
        job_title: str = employee_info.get('job_title')
        reports_to: str = employee_info.get('reports_to', reports_to_default)
        reports_to_card_id: str = card_id_by_employee[reports_to]

        component = EmployeeCardComponent(
            code=None,
            firstName=first_name,
            lastName=last_name, 
            displayName=employee_full_name,
            jobTitle=job_title,
            email=email,
            state="Active",
            type="Regular",
            isManager=is_manager,
            company=company_card_id,
            reportsTo=reports_to_card_id
        )

        schema = EmployeeCardComponent.schema(
            only=(
                'FirstName',
                'LastName',
                'DisplayName',
                'JobTitle',
                'Email',
                'State',
                'Type',
                'IsManager',
                'Company',
                'ReportsTo',
                )
            )

        component_dump: Dict = schema.dump(component)
        card_id: int = cmdbuild_client.create(component_data=component_dump)
        card_id_by_employee[employee_full_name] = card_id