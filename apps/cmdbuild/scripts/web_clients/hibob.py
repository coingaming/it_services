

from requests import get as get_response
from typing import Dict, Optional, Generator, Any


class HiBobWebClient:

    def __init__(self, url: str, token: str):
        self.__url = url
        self.__token = token

    def pull(self, chunk_size: int = 1024, stream=True) -> Any[Generator, Dict]:
        headers: Dict = {
            "Accept": "application/json", 
            "Authorization": self.__token
        }
        payload: Optional[Dict] = None
        with get_response(self.__url, headers=headers, stream=True) as r:
            r.raise_for_status()
            payload = r.json()
            #yield from r.iter_content(chunk_size)
        return payload