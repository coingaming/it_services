from typing import List, Dict, Optional
from marshmallow import Schema, fields, validate
from ..constants import ClassType, ClassAttributeType


class ClassModel:

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


class ClassSchema(Schema):
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
    uiRouting_custom = fields.Dict()
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


class ClassAttributeModel:

    __slots__ = (
        '_id'
        'type'
        'name'
        'description'
        '_description_translation'
        'showInGrid'
        'showInReducedGrid'
        'unique'
        'mandatory'
        'inherited'
        'active'
        'index'
        'defaultValue'
        'group'
        '_group_description'
        '_group_description_translation'
        'mode'
        'writable'
        'immutable'
        'hidden'
        '_can_read'
        '_can_create'
        '_can_update'
        '_can_modify'
        'metadata'
        'help'
        'showIf'
        'validationRules'
        'autoValue'
        'alias'
        'syncToDmsAttr'
        'helpAlwaysVisible'
        'hideInFilter'
        'virtual'
        '_permissions'
        'password'
        'showPassword'
        'textContentSecurity'
        '_html'
        'maxLength'
        'multiline'
    )

    _id: str
    type: str #
    name: str
    description: str
    _description_translation: str
    showInGrid: bool
    showInReducedGrid: bool
    unique: bool
    mandatory: bool
    inherited: bool
    active: bool
    index: int
    defaultValue: Optional(str)
    group: str
    _group_description: str
    _group_description_translation: str
    mode: str
    writable: bool
    immutable: bool
    hidden: bool
    _can_read: bool
    _can_create: bool
    _can_update: bool
    _can_modify: bool
    metadata: Dict
    help: Optional(str)
    showIf: Optional(str)
    validationRules: Optional(str)
    autoValue: Optional(str)
    alias: Optional(str)
    syncToDmsAttr: Optional(str)
    helpAlwaysVisible: bool
    hideInFilter: bool
    virtual: bool
    _permissions: str
    password: bool
    showPassword: str
    textContentSecurity: str
    _html: bool
    maxLength: int
    multiline: bool


class ClassAttributeSchema(Schema):
    name = fields.String(required=True)
    type = fields.String(required=True, validate=validate.OneOf(ClassAttributeType.RANGE))
    description = fields.String(required=True)
    unique = fields.Boolean()
    mandatory = fields.Boolean(default=True)
    inherited = fields.Boolean()
    active = fields.Boolean(default=True)
    _id = fields.String()
    _description_translation = fields.String()
    showInGrid = fields.Boolean()
    showInReducedGrid = fields.Boolean()
    index = fields.Integer()
    defaultValue = fields.String(allow_none=True)
    group = fields.String()
    _group_description = fields.String()
    _group_description_translation = fields.String()
    mode = fields.String()
    writable = fields.Boolean()
    immutable = fields.Boolean()
    hidden = fields.Boolean()
    _can_read = fields.Boolean()
    _can_create = fields.Boolean()
    _can_update = fields.Boolean()
    _can_modify = fields.Boolean()
    metadata = fields.Dictionary()
    help = fields.String(allow_none=True)
    showIf = fields.String(allow_none=True)
    validationRules = fields.String(allow_none=True)
    autoValue = fields.String(allow_none=True)
    alias = fields.String(allow_none=True)
    syncToDmsAttr = fields.String(allow_none=True)
    helpAlwaysVisible = fields.Boolean()
    hideInFilter = fields.Boolean()
    virtual = fields.Boolean()
    _permissions = fields.String()
    password = fields.Boolean()
    showPassword = fields.String()
    textContentSecurity = fields.String()
    _html = fields.Boolean()
    maxLength = fields.Integer()
    multiline = fields.Boolean()