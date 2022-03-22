
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