from typing import List, Dict, Optional
from marshmallow import Schema, fields, validate
from ..constants import ClassType


class ClassComponent:

    __slots__ = (
        '_id'
        'name'
        'description'
        '_description_translation'
        '_description_plural_translation'
        'prototype'
        'parent'
        'active'
        'type'
        'speciality'
        '_can_read'
        '_can_create'
        '_can_update'
        '_can_clone'
        '_can_delete'
        '_can_modify'
        '_can_print'
        '_can_bulk_update'
        '_can_bulk_delete'
        '_relgraph_access'
        '_attachment_access'
        '_detail_access'
        '_email_access'
        '_history_access'
        '_note_access'
        '_relation_access'
        '_schedule_access'
        'defaultFilter'
        'defaultImportTemplate'
        'defaultExportTemplate'
        'description_attribute_name'
        'metadata'
        '_icon'
        'uiRouting_mode'
        'uiRouting_target'
        'uiRouting_custom'
        'dmsCategory'
        'noteInline'
        'noteInlineClosed'
        'attachmentsInline'
        'attachmentsInlineClosed'
        'validationRule'
        'stoppableByUser'
        'defaultOrder'
        'domainOrder'
        'help'
        '_help_translation'
        'widgets'
        'formTriggers'
        'contextMenuItems'
        'attributeGroups'
    )

    _id: str
    name: str
    description: str
    _description_translation: str
    _description_plural_translation: str
    prototype: bool
    parent: str
    active: bool
    type: str
    speciality: str
    _can_read: bool
    _can_create: bool
    _can_update: bool
    _can_clone: bool
    _can_delete: bool
    _can_modify: bool
    _can_print: bool
    _can_bulk_update: bool
    _can_bulk_delete: bool
    _relgraph_access: bool
    _attachment_access: bool
    _detail_access: bool
    _email_access: bool
    _history_access: bool
    _note_access: bool
    _relation_access: bool
    _schedule_access: bool
    defaultFilter: Optional(str)
    defaultImportTemplate: Optional(str)
    defaultExportTemplate: Optional(str)
    description_attribute_name: str
    metadata: Dict
    _icon: int
    uiRouting_mode: str
    uiRouting_target: Optional(str)
    uiRouting_custom: Dict
    dmsCategory: Optional(str)
    noteInline: bool
    noteInlineClosed: bool
    attachmentsInline: bool
    attachmentsInlineClosed: bool
    validationRule: Optional(str)
    stoppableByUser: bool
    defaultOrder: List
    domainOrder: List
    help: Optional(str)
    _help_translation :str
    widgets: List
    formTriggers: List
    contextMenuItems: List
    attributeGroups: List


class ClassComponent(Schema):
    name = fields.String(required=True)
    description = fields.String(required=True)
    prototype = fields.Boolean(default=False) # Superclass (in cmdbuild)
    active = fields.Boolean(default=True)
    parent = fields.String(default=None) # Inherits from (in cmdbuild)
    type = fields.String(validate=validate.OneOf(ClassType.RANGE))
    _id= fields.String()
    _description_translation = fields.String()
    _description_plural_translation = fields.String()
    speciality = fields.String()
    _can_read = fields.Boolean()
    _can_create = fields.Boolean()
    _can_update = fields.Boolean()
    _can_clone = fields.Boolean()
    _can_delete = fields.Boolean()
    _can_modify = fields.Boolean()
    _can_print = fields.Boolean()
    _can_bulk_update = fields.Boolean()
    _can_bulk_delete = fields.Boolean()
    _relgraph_access = fields.Boolean()
    _attachment_access = fields.Boolean()
    _detail_access = fields.Boolean()
    _email_access = fields.Boolean()
    _history_access = fields.Boolean()
    _note_access = fields.Boolean()
    _relation_access = fields.Boolean()
    _schedule_access = fields.Boolean()
    defaultFilter = fields.String()
    defaultImportTemplate = fields.String()
    defaultExportTemplate = fields.String()
    description_attribute_name = fields.String()
    metadata = fields.Dictionary()
    _icon = fields.Integer()
    uiRouting_mode = fields.String()
    uiRouting_target = fields.String()
    uiRouting_custom: Dict
    dmsCategory = fields.String()
    noteInline = fields.Boolean()
    noteInlineClosed = fields.Boolean()
    attachmentsInline = fields.Boolean()
    attachmentsInlineClosed = fields.Boolean()
    validationRule = fields.String()
    stoppableByUser = fields.Boolean()
    defaultOrder = fields.List()
    domainOrder = fields.List()
    help = fields.String()
    _help_translation = fields.String()
    widgets = fields.List()
    formTriggers = fields.List()
    contextMenuItems = fields.List()
    attributeGroups = fields.List()