from requests import Response
from typing import Dict, List, NoReturn
from .base import BaseComponent


class Domain(BaseComponent):

    path: str = "services/rest/v3/domains"
    schema = None
