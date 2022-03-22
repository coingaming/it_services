from .base import BaseComponent, BaseAttribute
from typing import Callable

class ClassComponent(BaseComponent):
    path: str = "services/rest/v3/classes"
    model = None
    schema = None


class ClassAttributes(BaseAttribute):
    path: Callable = lambda classId: f"services/rest/v3/classes/{classId}/attributes"
    model = None
    schema = None