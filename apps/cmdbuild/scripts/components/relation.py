from typing import Callable, Tuple, Optional
from scripts.components.base import BaseComponent, BaseValues
from scripts.schemas.relation import RelationSchema


class RelationComponent:

    schema = RelationSchema

    __slots__ = (
        '_type',
        '_destinationId',
        '_destinationType',
        '_sourceType',
        '_sourceId',
        '_is_direct',
        '_destinationDescription',
        '_destinationCode',
    )

    def __init__(
        self,
        domain_name: str,
        destinationId: str,
        destinationType: str,
        sourceType: str,
        sourceId: str,
        is_direct: str,
        destinationDescription: str,
        destinationCode: str
    ):

        self._type = domain_name
        self._destinationId = destinationId
        self._destinationType = destinationType
        self._sourceType = sourceType
        self._sourceId = sourceId
        self._is_direct = is_direct
        self._destinationDescription = destinationDescription
        self._destinationCode = destinationCode