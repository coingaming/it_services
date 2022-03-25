from typing import Tuple
from xml import dom
from scripts.schemas.class_component import ClassModelSchema, ClassAttributeSchema
from scripts.common.constants import ClassType, AttributeMode, AttributeType


class ClassModel:

    schema = ClassModelSchema()

    __slots__ = (
        'name',
        'description',
        'prototype',
        'parent',
        'active',
        'type',
        'attributes'
    )

    def __init__(
        self,    
        name: str,
        attributes: Tuple["ClassAttributeModel"],
        description: str="",
        prototype: str="false",
        parent: str="false",
        active: bool="true",
        type: str=ClassType.STANDART,
    ):
        self.name = name
        self.description = description
        self.prototype = prototype
        self.parent = parent
        self.active = active
        self.type = type
        self.attributes = attributes


class ClassAttributeModel:

    schema = ClassAttributeSchema()

    __slots__ = (
        'name',
        'type',
        'description',
        'mode',
        'unique',
        'mandatory',
        'active',
        'showInGrid',
        'group',
        'domain',
        'direction'
    )

    def __init__(
        self,
        name: str,
        type: AttributeType,
        description: str,
        mode: AttributeMode = AttributeMode.EDITABLE,
        group: str = "null",
        unique: str = "false",
        mandatory: str = "false",
        active: str = "true",
        showInGrid: str = "true",
        domain: str = "null",
        direction: str = "null"
    ):
        self.name = name
        self.type = type
        self.description = description
        self.mode = mode
        self.group = group
        self.unique = unique
        self.mandatory = mandatory
        self.active = active
        self.showInGrid = showInGrid
        self.domain = domain
        self.direction = direction