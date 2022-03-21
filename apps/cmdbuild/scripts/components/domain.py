from requests import Response, Session
from typing import Dict, List, NoReturn
from .base import BaseComponent


class Domain(BaseComponent):

    path: str = "services/rest/v3/domains"


    def create(self, domain_data: Dict)-> NoReturn:
        url: str = f"{self.base_url}/{self.path}"
        response: Response = self.session.post(
            url,
            headers=self.auth_header,
            json=domain_data
        )
        response.raise_for_status()


    def update(self, domain_id: str, domain_data: Dict)-> NoReturn:
        url: str = f"{self.base_url}/{self.path}/{domain_id}"
        response: Response = self.session.put(
            url,
            headers=self.auth_header,
            json=domain_data
        )
        response.raise_for_status()


    def delete(self, domain_id: str)-> NoReturn:
        url: str = f"{self.base_url}/{self.path}/{domain_id}"
        response: Response = self.session.delete(
            url,
            headers=self.auth_header,
        )
        response.raise_for_status()


    def get_details(self, domain_id: str)-> Dict:
        url: str = f"{self.base_url}/{self.path}/{domain_id}"
        response: Response = self.session.get(
            url,
            headers=self.auth_header,
        )
        response.raise_for_status()


    def get_all(self, filter: str, limit: int, start: int)-> List:
        url: str = f"{self.base_url}/{self.path}"
        response: Response = self.session.get(
            url,
            headers=self.auth_header,
        )
        response.raise_for_status()
        response_payload: Dict = response.json()
        domain_list: List = response_payload['data']
        return domain_list
