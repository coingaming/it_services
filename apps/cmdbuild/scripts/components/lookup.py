
from typing import Callable, Tuple, Optional
from scripts.components.base import BaseComponent, BaseValues
from scripts.schemas.lookup import LookupSchema


class LookupModel:

    schema = LookupSchema()

    __slots__ = (
        'name',
        'attributes',
    )

    def __init__(
        self, 
        name: str,
        attributes: Tuple["LookupAttributeModel"]
    ):
        self.name = name
        self.attributes = attributes


class LookupAttributeModel:

    __slots__ = (
        'code',
        'description',
        'active',
        'note',
     )

    def __init__(
        self,
        code: str,
        description: str,
        active: str="true",
        note: str="",
    ):
        self.code = code
        self.description = description
        self.active = active
        self.note = note