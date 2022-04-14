from logging import Logger
from typing import NoReturn, Dict, List, Tuple
from scripts.web_clients.cmdbuild import CmdBuildWebClient
from scripts.components.lookup import LookupModel, LookupAttributeModel
from scripts.components.domain import DomainModel
from scripts.components.class_component import ClassAttributeModel
from scripts.common.constants import CascadeActionTypes, AttributeType, CardinalityTypes
from scripts.web_clients.hibob import HiBobWebClient

from . import glossary_4_5
from . import glossary_5_6
from . import glossary_6_7
from . import glossary_7_8


_CURRENT_VERSION = 1


def _update_from_1_to_2(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
    ) -> NoReturn:

    components: Tuple[DomainModel] = (
        DomainModel(
            name="EmployeeManager",
            description="EmployeeManager",
            source="Employee",
            destination="Employee",
            cardinality=CardinalityTypes.ONE_TO_MANY,
            descriptionDirect="direct reports to", # is manager of
            descriptionInverse="reports to", # is managed by
            cascadeActionDirect = CascadeActionTypes.DO_NOT_DELETE_IF_HAS_RELATIONS,
            cascadeActionInverse = CascadeActionTypes.DELETE_RELATION
        ),

        DomainModel(
            name="ServiceAdminService",
            description="ServiceAdminService",
            source="Employee",
            destination="Service",
            cardinality=CardinalityTypes.MANY_TO_MANY,
            descriptionDirect="is service admin of",
            descriptionInverse="has as service admin",
            cascadeActionDirect = CascadeActionTypes.DELETE_RELATION,
            cascadeActionInverse = CascadeActionTypes.DELETE_RELATION
        ),

        DomainModel(
            name="ServiceAccessService",
            description="ServiceAccessService",
            source="Employee",
            destination="Service",
            cardinality=CardinalityTypes.MANY_TO_MANY,
            descriptionDirect="has access to service",
            descriptionInverse="is accessible by",
            cascadeActionDirect = CascadeActionTypes.DELETE_RELATION,
            cascadeActionInverse = CascadeActionTypes.DELETE_RELATION
        ),
    )

    for component in components:
        dump: Dict = DomainModel.schema.dump(component)
        cmdbuild_client.path = "rest/v3/domains"
        cmdbuild_client.create(component_data=dump)
        logger.info(f'Domain {component.name} is created')


def _update_from_2_to_3(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
    ) -> NoReturn:

    components: Tuple[ClassAttributeModel] = (
        ClassAttributeModel(
            name="ReportsTo",
            type=AttributeType.REFERENCE,
            description="Reports to",
            group="Employee - Administrative Data", # todo define component
            domain="EmployeeManager",
            direction="inverse"
        ),
        ClassAttributeModel(
            name="IsManager",
            type=AttributeType.BOOLEAN,
            description="Is Manager",
            group="Employee - Administrative Data", # todo define component
        ),
        ClassAttributeModel(
            name="DisplayName",
            type=AttributeType.STRING,
            description="DisplayName",
            group="Employee - General Data", # todo define component
        ),
        ClassAttributeModel(
            name="JobTitle",
            type=AttributeType.STRING,
            description="Job Title",
            group="Employee - General Data", # todo define component
        ),
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

    glossary_4_5.create_cards(hibob_client, cmdbuild_client, logger)


def _update_from_5_to_6(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
    ) -> NoReturn:

    glossary_5_6.create_services_cards(hibob_client, cmdbuild_client, logger)


def _update_from_6_to_7(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
    ) -> NoReturn:

    glossary_6_7.establish_access_relations(hibob_client, cmdbuild_client, logger)


def _update_from_7_to_8(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient,
    logger: Logger
    ) -> NoReturn:

    glossary_7_8.create_edufy_cards(hibob_client, cmdbuild_client, logger)


_versionUpdaters = {
    1: _update_from_1_to_2,
    2: _update_from_2_to_3,
    3: _update_from_3_to_4,
    4: _update_from_5_to_6,
    5: _update_from_6_to_7,
    6: _update_from_7_to_8,
}


def update_version(
    hibob_client: HiBobWebClient,
    cmdbuild_client: CmdBuildWebClient, 
    logger: Logger
    ) -> NoReturn:

    version: int = _CURRENT_VERSION

    try:
        while version in _versionUpdaters:
            logger.info(f"Applying version = {version}")
            _versionUpdaters[version](hibob_client, cmdbuild_client, logger)
            version += 1
    except Exception as err:
        print('exception message ', err)