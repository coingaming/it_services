
from typing import Callable
from apps.cmdbuild.scripts.components.base import BaseComponent, BaseValues


class Lookup(BaseComponent):
    path: str = "services/rest/v3/lookup_types"
    model = None
    schema = None


class LookupValues(BaseValues):
    path: Callable = lambda lookupTypeId: f"services/rest/v3/lookup_types/{lookupTypeId}/values"
    model = None
    schema = None