
class CardinalityTypes:
    one_to_one: str = "1:1"
    one_to_many: str = "1:N"
    many_to_one: str = "N:1"
    many_to_many: str = "N:N"


class CascadeActionTypes:
    do_not_delete_if_has_relations: str = "restrict"
    delete_relation: str = "setnull"
    delete_also_related_cards: str = "delete"
    