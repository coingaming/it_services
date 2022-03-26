import pandas as pd
from logging import Logger
from typing import NoReturn, Dict, List, Tuple
from scripts.web_clients.cmdbuild import CmdBuildWebClient
from scripts.components.lookup import LookupModel, LookupAttributeModel
from scripts.components.domain import DomainModel
from scripts.common.constants import CascadeActionTypes
from scripts.components.class_component import ClassAttributeModel
from scripts.common.constants import CascadeActionTypes, AttributeType
from scripts.web_clients.hibob import HiBobWebClient
from .glossary_4_5 import EMPLOYEE_FRAME_COLUMNS


_CURRENT_VERSION = 4


def _update_from_0_to_1(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
    ) -> NoReturn:

    components: Tuple = (
        LookupModel(
            name="Service - Risk",
            attributes=(
                LookupAttributeModel(code="High", description="High"), 
                LookupAttributeModel(code="Medium", description="Medium"),
                LookupAttributeModel(code="Low", description="Low"),
            )
        ),
        LookupModel(
            name="Service - Category",
            attributes=(
                LookupAttributeModel(code="CoreInfrastructure", description="Core Infrastructure"),
                LookupAttributeModel(code="Backoffice", description="Backoffice"),
                LookupAttributeModel(code="Projectmanagement", description="Project management"),
                LookupAttributeModel(code="Other", description="Other"),
                LookupAttributeModel(code="DesignTools", description="Design Tools"),
                LookupAttributeModel(code="TestingTool", description="Testing Tool"),
                LookupAttributeModel(code="SessionRecording", description="Session Recording"),
                LookupAttributeModel(code="MarketingTool", description="Marketing Tool"),
                LookupAttributeModel(code="Payments", description="Payments"),
                LookupAttributeModel(code="Communication", description="Communication"),
                LookupAttributeModel(code="ReportingTool", description="Reporting Tool"),
                LookupAttributeModel(code="DevelopmentTool", description="Development Tool"),
                LookupAttributeModel(code="DatabaseTool", description="Database Tool"),
                LookupAttributeModel(code="Security", description="Security"),
                LookupAttributeModel(code="Assets", description="Assets"),
                LookupAttributeModel(code="GrammarTools", description="Grammar Tools"),
                LookupAttributeModel(code="DeviceManagement", description="Device Management"),
                LookupAttributeModel(code="ImageProcessingTool", description="Image Processing Tool"),
                LookupAttributeModel(code="Learning", description="Learning"),
                LookupAttributeModel(code="SEOTool", description="SEO Tool"),
                LookupAttributeModel(code="IdentityHub", description="Identity Hub"),
            )
        ),
        LookupModel(
            name="Service - Roles",
            attributes=(
                LookupAttributeModel(code="Admin", description="Admin"),
                LookupAttributeModel(code="User", description="User"),
                LookupAttributeModel(code="Guest", description="Guest"),
            )
        )
    )

    cmdbuild_client.path = "rest/v3/lookup_types"
    for model in components:
        dump: Dict = model.schema.dump(model)
        attributes_dump: List = dump.pop("attributes")
        # create lookup model
        cmdbuild_client.create(component_data=dump)
        # adding lookup atributes
        for item_dump in attributes_dump:
            cmdbuild_client.path = f"rest/v3/lookup_types/{model.name}/values"
            cmdbuild_client.create(component_data=item_dump)
        logger.info(f"Lookup {model.name} is created")


def _update_from_1_to_2(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
    ) -> NoReturn:

    component: DomainModel = DomainModel( # todo "reports to" class attribute
        name="EmployeeManager",
        description="EmployeeManager",
        source="Employee",
        destination="Employee",
        cardinality="1:N",
        descriptionDirect="direct reports to", # is manager of
        descriptionInverse="reports to", # is managed by
        cascadeActionDirect = CascadeActionTypes.DO_NOT_DELETE_IF_HAS_RELATIONS,
        cascadeActionInverse = CascadeActionTypes.DELETE_RELATION
    )
    dump: Dict = DomainModel.schema.dump(component)
    cmdbuild_client.path = "/rest/v3/domains"
    cmdbuild_client.create(component_data=dump)
    logger.info(f'Domain {component.name} is created')


def _update_from_2_to_3(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
    ) -> NoReturn:

    components: Tuple = (
        ClassAttributeModel(
            name="ReportsTo",
            type=AttributeType.REFERENCE,
            description="Reports to",
            group="Employee - Administrative Data", # todo define component
            domain="EmployeeManager",
            direction="inverse"
        ),
        ClassAttributeModel(
            name="OwnerOf",
            type=AttributeType.REFERENCE,
            description="Owner of",
            group="Employee - Administrative Data", # todo define component
            domain="ServiceOwnerService",
            direction="inverse"
        )
    )
    classId: str = "Employee"
    cmdbuild_client.path = f"rest/v3/classes/{classId}/attributes"
    for component in components:
        dump: Dict = ClassAttributeModel.schema.dump(component)
        cmdbuild_client.create(component_data=dump)
        logger.info(f'Attribute {component.name} is added to {classId} class')


def _update_from_3_to_4(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
    ) -> NoReturn:

    components: Tuple = (
        ClassAttributeModel(
            name="ReportsTo",
            type=AttributeType.REFERENCE,
            description="Reports to",
            group="Employee - Administrative Data",
            domain="EmployeeManager",
            direction="inverse"
        ),
        ClassAttributeModel(
            name="OwnerOf",
            type=AttributeType.REFERENCE,
            description="Owner of",
            group="Employee - Administrative Data",
            domain="ServiceOwnerService",
            direction="inverse"
        )
    )
    classId: str = "Employee"
    cmdbuild_client.path = f"rest/v3/classes/{classId}/attributes"

    for component in components:
        dump: Dict = ClassAttributeModel.schema.dump(component)
        cmdbuild_client.create(
            component_data=dump
        )
        logger.info(f'Attribute {component.name} is added to {classId} class')


def _update_from_4_to_5(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
    ) -> NoReturn:

    payload: Dict = hibob_client.pull(stream=False)
    employee_df: pd.DataFrame = pd.DataFrame(
        columns=[e.value for e in EMPLOYEE_FRAME_COLUMNS]
    )

    for row_idx, item in enumerate(payload['employees']):
        match item:
            case {
                'id': employee_id, 
                'firstName': first_name, 
                'secondName': second_name, 
                'email': email,
                'work': {
                    'isManager': is_manager, 
                    'reportsTo': {
                        'email': manager_email, 
                        'surname': manager_surname, 
                        'firstName': manager_first_name, 
                        'id': manager_id
                    }, 
                    'title': title, 
                    'department': department, 
                    'customColumns': custom_columns
                }
            }:

                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.ID] = employee_id
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.FIRST_NAME] = first_name
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.SECOND_NAME] = second_name
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.EMAIL] = email
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.IS_MANAGER] = is_manager
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.REPORT_TO] = manager_id
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.TITLE] = title
                employee_df.loc[row_idx, EMPLOYEE_FRAME_COLUMNS.DEPARTMENT] = department

    departments: List = employee_df[EMPLOYEE_FRAME_COLUMNS.DEPARTMENT].unique()



_versionUpdaters = {
	0: _update_from_0_to_1,
    1: _update_from_1_to_2,
    2: _update_from_2_to_3,
    3: _update_from_3_to_4,
    4: _update_from_4_to_5,
}


def update_version(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
    ) -> NoReturn:
    
    version: int = _CURRENT_VERSION
    while version in _versionUpdaters:
        logger.info(f"Applying version = {version}")
        _versionUpdaters[version](hibob_client, cmdbuild_client, logger)
        version += 1
