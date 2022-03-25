
class CardinalityTypes:
    ONE_TO_ONE: str = "1:1"
    ONE_TO_MANY: str = "1:N"
    MANY_TO_ONE: str = "N:1"
    MANY_TO_MANY: str = "N:N"
    RANGE = (ONE_TO_ONE, ONE_TO_MANY, MANY_TO_ONE, MANY_TO_MANY)


class CascadeActionTypes:
    DO_NOT_DELETE_IF_HAS_RELATIONS: str = "restrict"
    DELETE_RELATION: str = "setnull"
    DELETE_ALSO_RELATED_CARDS: str = "delete"
    RANGE: tuple = (DO_NOT_DELETE_IF_HAS_RELATIONS, DELETE_RELATION, DELETE_ALSO_RELATED_CARDS)


class ClassType:
    STANDART: str = "standard"
    SIMPLE: str = "simple"
    RANGE: tuple = (STANDART, SIMPLE)


class AttributeType:
    BIGINTEGER: str = "long" # todo write "Unit of measure"
    BOOLEAN: str = "boolean"
    CHAR: str = "char"
    DATE: str = "date"
    DECIMAL: str = "decimal" # todo choose "Precision Scale" lookup
    DOUBLE: str = "double" # todo write "Unit of measure"
    FILE: str = "file" # todo choose "DMS category" [Document, Image] lookup
    FORMULA: str = "formula" # todo choose "Function type" [Function, Script] lookup
    INTEGER: str = "integer" # todo write "Unit of measure"
    IP_ADDRESS: str = "ipAddress" # todo choose "Choose ip type" lookup
    LINK: str = "link" # todo set bool "Show label"
    LOOKUP: str = "lookup" # todo set link to lookup class 
    LOOKUPARRAY: str = "lookupArray" # todo set lookup link
    REFERENCE: str = "reference" # todo set domain link 
    STRING: str = "string" # todo choose "Editor type" [default, password] lookup, "Max Length"
    TEXT: str = "text" # todo choose "Type" [Plain text, Editor HTML, Editor MARKDOWN] lookup
    TIME: str = "time" # todo set bool "Show second"
    TIMESTAMP: str = "dateTime" # todo set bool "Show second"
    RANGE: tuple = (BIGINTEGER, BOOLEAN, CHAR, DATE, DECIMAL, DOUBLE, FILE, FORMULA, INTEGER, IP_ADDRESS, \
        LINK, LOOKUP, LOOKUPARRAY, REFERENCE, STRING, TEXT, TIME, TIMESTAMP)


class AttributeMode:
    EDITABLE: str = "write"
    READ_ONLY: str = "read"
    HIDDEN: str = "hidden"
    IMMUTABLE: str = "immutable"
    RANGE: tuple = (EDITABLE, READ_ONLY, HIDDEN, IMMUTABLE)