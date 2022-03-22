from requests import Response
from typing import Dict, List, NoReturn
from .base import BaseComponent


class ClassComponent(BaseComponent):


    path: str = "services/rest/v3/classes"
    schema = None