from typing import List, Optional
from typing_extensions import Required
from marshmallow import Schema, fields, validate


class LookupModel:

    __slots__ = (
        'id'
        'name'
        'parent'
        'speciality'
        'accessType'
    )

    _id: str
    name: str
    parent: Optional(str)
    speciality: str
    accessType: str


class LookupSchema(Schema):
    _id = fields.String()
    name = fields.String(required=True)
    parent = fields.String(allow_none=True)
    speciality = fields.String(default="default")
    accessType = fields.String(default="default")


class LookupValueModel:
    __slots__ = (
        '_id',
        '_type',
        'code',
        'description',
        '_description_translation',
        'index',
        'active',
        'parent_id',
        'parent_type',
        'default',
        'note',
        'text_color',
        'icon_type',
        'icon_image',
        'icon_font',
        'icon_color',
        'accessType'
    )

    _id: int
    _type: str
    code: str
    description: str
    _description_translation: str
    index: int
    active: bool
    parent_id: Optional(str)
    parent_type: Optional(str)
    default: bool
    note: Optional(str)
    text_color: Optional(str)
    icon_type: str
    icon_image: Optional(str)
    icon_font: Optional(str)
    icon_color: Optional(str)
    accessType: str


class LookupValueSchema(Schema):
    _id = fields.Integer()
    _type = fields.String()
    code = fields.String(required=True)
    description = fields.String(required=True)
    _description_translation = fields.String()
    index = fields.Integer()
    active = fields.Boolean()
    parent_id = fields.String()
    parent_type = fields.String()
    default = fields.Boolean()
    note = fields.String()
    text_color = fields.String()
    icon_type = fields.String()
    icon_image = fields.String()
    icon_font = fields.String()
    icon_color = fields.String()
    accessType = fields.String()