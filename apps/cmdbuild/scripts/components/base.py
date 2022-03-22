from typing import Dict, NoReturn, List
from requests import Session, Response


class BaseComponent:
    session: Session
    base_url: str
    auth_header: str

    path = ""
    model = None
    schema = None


    def __init__(self, session: Session, base_url: str, auth_header: Dict):
        self.session = session
        self.base_url = base_url
        self.auth_header = auth_header


    def create(self, component_data: Dict)-> NoReturn:
        url: str = f"{self.base_url}/{self.path}"
        response: Response = self.session.post(
            url,
            headers=self.auth_header,
            json=component_data
        )
        response.raise_for_status()


    def update(self, component_id: str, component_data: Dict)-> NoReturn:
        url: str = f"{self.base_url}/{self.path}/{component_id}"
        response: Response = self.session.put(
            url,
            headers=self.auth_header,
            json=component_data
        )
        response.raise_for_status()


    def delete(self, component_id: str)-> NoReturn:
        url: str = f"{self.base_url}/{self.path}/{component_id}"
        response: Response = self.session.delete(
            url,
            headers=self.auth_header,
        )
        response.raise_for_status()


    def get_details(self, component_id: str)-> Dict:
        url: str = f"{self.base_url}/{self.path}/{component_id}"
        response: Response = self.session.get(
            url,
            headers=self.auth_header,
        )
        response.raise_for_status()


class BaseAttribute(BaseComponent):
    def reorder(self, attr_order: List[str]):
        url: str = f"{self.base_url}/{self.path}/order"
        response: Response = self.session.post(
            url,
            headers=self.auth_header,
        )
        response.raise_for_status()


class BaseValues(BaseComponent):
    def reorder(self, values_order: List[int]):
        url: str = f"{self.base_url}/{self.path}/order"
        response: Response = self.session.post(
            url,
            headers=self.auth_header,
        )
        response.raise_for_status()