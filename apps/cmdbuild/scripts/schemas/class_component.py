from marshmallow import Schema, fields, validate
from ..common.constants import ClassType, AttributeType, AttributeMode


class ClassAttributeSchema(Schema):
    name = fields.String(required=True)
    type = fields.String(required=True, validate=validate.OneOf(AttributeType.RANGE))
    description = fields.String(required=True)
    mode = fields.String(default=AttributeMode.EDITABLE, validate=validate.OneOf(AttributeMode.RANGE))
    unique = fields.String()
    mandatory = fields.String()
    active = fields.String()
    showInGrid = fields.String()
    group = fields.String()
    # optional, filtering by only=(...)
    domain = fields.String()
    direction = fields.String()


class ClassModelSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(required=True)
    prototype = fields.String() # Superclass (in cmdbuild)
    active = fields.String()
    parent = fields.String() # Inherits from (in cmdbuild)
    type = fields.String(validate=validate.OneOf(ClassType.RANGE))
    attributes = fields.Nested(ClassAttributeSchema, many=True)

    
    