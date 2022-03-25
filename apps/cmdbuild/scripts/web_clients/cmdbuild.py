from typing import Dict, NoReturn,  Optional
from requests import Session, Response
from logging import Logger

class CmdBuildWebClient:

    def __init__(
        self, 
        session: Session, 
        base_url: str, 
        path: Optional[str] = None,
        logger: Optional[Logger] = None,
    ):
        self.__session = session
        self.__base_url = base_url
        self.__path = path
        self.__logger = logger
        self.__auth_header: Optional[Dict] = None
        

    @property
    def path(self):
        return self.__path


    @path.setter
    def path(self, path):
        self.__path = path


    def generate_session_token(self, username, password) -> str:

        """
            Every request requires the user to specify in the header the field “Cmdbuild-authorization”, that
            field is a session token generated when creating a session.
            method: post
            url: http://hostname:port/cmdbuild/services/rest/v3/sessions?scope=service&returnId=true
        """

        self.__logger.info("Generating session authentication token")
        response: Response = self.__session.post(
            f"{self.__base_url}/{self.__path}",
            json={
                "username": username, 
                "password": password
            }
        )

        response.raise_for_status()
        response_payload: Dict = response.json()
        token = response_payload['data']['_id']
        self.__auth_header = {
            "Cmdbuild-authorization": token
        }
        self.__logger.info(f"Authentication token is generated: {token}")


    def create(self, component_data: Dict)-> NoReturn:
        assert self.__auth_header is not None, "Need to generate an authentication token"
        url: str = f"{self.__base_url}/{self.__path}"
        response: Response = self.__session.post(
            url,
            headers=self.__auth_header,
            json=component_data
        )
        response.raise_for_status()


    def update(self, component_id: str, component_data: Dict)-> NoReturn:
        assert self.__auth_header is not None, "Need to generate an authentication token"
        url: str = f"{self.__base_url}/{self.__path}/{component_id}"
        response: Response = self.__session.put(
            url,
            headers=self.__auth_header,
            json=component_data
        )
        response.raise_for_status()


    def delete(self, component_id: str)-> NoReturn:
        assert self.__auth_header is not None, "Need to generate an authentication token"
        url: str = f"{self.__base_url}/{self.__path}/{component_id}"
        response: Response = self.__session.delete(
            url,
            headers=self.__auth_header,
        )
        response.raise_for_status()


    def get_details(self, component_id: str)-> Dict:
        assert self.__auth_header is not None, "Need to generate an authentication token"
        url: str = f"{self.__base_url}/{self.__path}/{component_id}"
        response: Response = self.__session.get(
            url,
            headers=self.__auth_header,
        )
        response.raise_for_status()