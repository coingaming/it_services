
from re import L
from apps.cmdbuild.scripts.components.base import BaseComponent



class Lookup(BaseComponent):

    path: str = "services/rest/v3/lookup_types"
    schema = None