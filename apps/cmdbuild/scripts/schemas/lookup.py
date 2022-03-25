from marshmallow import Schema, fields


class LookupAttributesSchema(Schema):
    code = fields.String(required=True)
    description = fields.String(required=True)
    active = fields.String(default="true")
    note = fields.String(default="")


class LookupSchema(Schema):
    name = fields.String(required=True)
    attributes = fields.Nested(LookupAttributesSchema, many=True)