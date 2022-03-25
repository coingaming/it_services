from .base import BaseComponent
from scripts.schemas.domain import DomainSchema


class DomainModel:

    schema = DomainSchema()

    __slots__ = (
        'name',
        'description',
        'source',
        'destination',
        'cardinality',
        'descriptionDirect',
        'descriptionInverse',
        'cascadeActionDirect',
        'cascadeActionInverse',
        'active',
    )

    def __init__(
        self,
        name: str,
        description: str,
        source: str,
        destination: str,
        cardinality: str,
        descriptionDirect: str,
        descriptionInverse: str,
        cascadeActionDirect: str,
        cascadeActionInverse: str,
        active: str="true"
    ):
        self.name = name
        self.description = description
        self.source = source
        self.destination = destination
        self.cardinality = cardinality
        self.descriptionDirect = descriptionDirect
        self.descriptionInverse = descriptionInverse
        self.cascadeActionDirect = cascadeActionDirect
        self.cascadeActionInverse = cascadeActionInverse
        self.active = active
