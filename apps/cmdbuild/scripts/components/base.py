
from typing import Dict, List, NoReturn
from requests import Session, Response


class BaseComponent:
    session: Session
    base_url: str
    auth_header: str
    path: str

    def __init__(self, session: Session, base_url: str, auth_header: Dict):
        self.session = session
        self.base_url = base_url
        self.auth_header = auth_header
    
    def create(self, **kwargs)-> NoReturn:
        raise NotImplemented

    def update(self, component_id: str, **kwargs)-> NoReturn:
        raise NotImplemented

    def delete(self, component_id: str)-> NoReturn :
        raise NotImplemented
    
    def get_details(self, domain_id: str)-> Dict:
        raise NotImplemented

    def get_all(self, filter: str, limit: int, start: int)-> List:
        raise NotImplemented