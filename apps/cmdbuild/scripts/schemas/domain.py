from email.policy import default
from typing import List
from marshmallow import Schema, fields


class Domain:

    __slots__ = (
        'name',
        'description',
        'source',
        'sources',
        'sourceProcess',
        'destination',
        'destinations',
        'destinationProcess',
        'cardinality',
        'descriptionDirect',
        '_descriptionDirect_translation',
        'descriptionInverse',
        '_descriptionInverse_translation',
        'indexDirect',
        'indexInverse',
        'descriptionMasterDetail',
        '_descriptionMasterDetail_translation',
        'filterMasterDetail',
        'isMasterDetail',
        'sourceInline',
        'sourceDefaultClosed',
        'destinationInline',
        'destinationDefaultClosed',
        'active',
        'disabledSourceDescendants',
        'disabledDestinationDescendants',
        'masterDetailAggregateAttrs',
        'cascadeActionDirect',
        'cascadeActionInverse',
        '_cascadeActionDirect_actual',
        '_cascadeActionInverse_actual',
        'cascadeActionDirect_askConfirm',
        'cascadeActionInverse_askConfirm',
        '_can_create',
    )

    name: str
    description: str
    source: str
    sources: List
    sourceProcess: bool
    destination: str
    destinations: List
    destinationProcess: bool
    cardinality: str
    descriptionDirect: str
    _descriptionDirect_translation: str
    descriptionInverse: str
    _descriptionInverse_translation: str
    indexDirect: int
    indexInverse: int
    descriptionMasterDetail: str
    _descriptionMasterDetail_translation: str
    filterMasterDetail: str
    isMasterDetail: bool
    sourceInline: bool
    sourceDefaultClosed: bool
    destinationInline: bool
    destinationDefaultClosed: bool
    active: bool
    disabledSourceDescendants: List
    disabledDestinationDescendants: List
    masterDetailAggregateAttrs: List
    cascadeActionDirect: str
    cascadeActionInverse: str
    _cascadeActionDirect_actual: str
    _cascadeActionInverse_actual: str
    cascadeActionDirect_askConfirm: bool
    cascadeActionInverse_askConfirm: bool
    _can_create: bool


class DomainSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(required=True)
    source = fields.String(required=True)
    destination = fields.String(required=True)
    cardinality = fields.String(required=True)
    descriptionDirect = fields.String(required=True)
    descriptionInverse = fields.String(required=True)
    cascadeActionDirect = fields.String(required=True)
    cascadeActionInverse = fields.String(required=True)
    active = fields.Boolean(default=True)
    sources = fields.List()
    sourceProcess = fields.Boolean()
    destinations = fields.List()
    destinationProcess = fields.Boolean()
    _descriptionDirect_translation = fields.String()
    _descriptionInverse_translation = fields.String()
    indexDirect = fields.Integer()
    indexInverse = fields.Integer()
    descriptionMasterDetail = fields.String()
    _descriptionMasterDetail_translation = fields.String()
    filterMasterDetail = fields.String()
    isMasterDetail = fields.Boolean()
    sourceInline = fields.Boolean()
    sourceDefaultClosed = fields.Boolean()
    destinationInline = fields.Boolean()
    destinationDefaultClosed = fields.Boolean()
    disabledSourceDescendants = fields.List()
    disabledDestinationDescendants = fields.List()
    masterDetailAggregateAttrs = fields.List()
    _cascadeActionDirect_actual = fields.String()
    _cascadeActionInverse_actual = fields.String()
    cascadeActionDirect_askConfirm = fields.Boolean()
    cascadeActionInverse_askConfirm = fields.Boolean()
    _can_create = fields.Boolean()