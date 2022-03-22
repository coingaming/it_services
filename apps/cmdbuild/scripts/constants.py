
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
    RANGE = (DO_NOT_DELETE_IF_HAS_RELATIONS, DELETE_RELATION, DELETE_ALSO_RELATED_CARDS)


class ClassType:
    STANDART: str = "standard"
    SIMPLE: str = "simple"
    RANGE = (STANDART, SIMPLE)


class ClassAttributeType:
    BIGINTEGER = "long" # todo write "Unit of measure"
    BOOLEAN = "boolean"
    CHAR = "char"
    DATE = "date"
    DECIMAL = "decimal" # todo choose "Precision Scale" lookup
    DOUBLE = "double" # todo write "Unit of measure"
    FILE = "file" # todo choose "DMS category" [Document, Image] lookup
    FORMULA = "formula" # todo choose "Function type" [Function, Script] lookup
    INTEGER = "integer" # todo write "Unit of measure"
    IP_ADDRESS = "ipAddress" # todo choose "Choose ip type" lookup
    LINK = "link" # todo set bool "Show label"
    LOOKUP = "lookup" # todo set link to lookup class 
    LOOKUPARRAY = "lookupArray" # todo set lookup link
    REFERENCE = "reference" # todo set domain link 
    STRING = "string" # todo choose "Editor type" [default, password] lookup, "Max Length"
    TEXT = "text" # todo choose "Type" [Plain text, Editor HTML, Editor MARKDOWN] lookup
    TIME = "time" # todo set bool "Show second"
    TIMESTAMP = "dateTime" # todo set bool "Show second"
    RANGE = (BIGINTEGER, BOOLEAN, CHAR, DATE, DECIMAL, DOUBLE, FILE, FORMULA, INTEGER, IP_ADDRESS, \
        LINK, LOOKUP, LOOKUPARRAY, REFERENCE, STRING, TEXT, TIME, TIMESTAMP)
