from marshmallow import Schema, fields, validate
from scripts.common.constants import CardinalityTypes, CascadeActionTypes


class DomainSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(required=True)
    source = fields.String(required=True)
    destination = fields.String(required=True)
    cardinality = fields.String(required=True, validate=validate.OneOf(CardinalityTypes.RANGE))
    descriptionDirect = fields.String(required=True)
    descriptionInverse = fields.String(required=True)
    cascadeActionDirect = fields.String(required=True, validate=validate.OneOf(CascadeActionTypes.RANGE))
    cascadeActionInverse = fields.String(required=True, validate=validate.OneOf(CascadeActionTypes.RANGE))
    active = fields.String(default="true")