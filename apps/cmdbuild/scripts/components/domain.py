import requests
from typing import Dict, List



class Domain:

    session: requests.Session
    ip_address: str
    token: str

    name: str
    description: str
    origin: str
    destination: str
    direct_description: str
    inverse_description: str
    cardinality: str

    path: str = "services/rest/v3/domains"
    header = {"Cmdbuild-authorization" : None}

    def __init__(self, url: str, token: str, ssl_cert: str):
        self.session = requests.Session()
        self.token = token
        self.url = url
        self.ssl_cert = ssl_cert
        # resp = session.get("https://18.202.182.116/ready2use-2.2-3.4/services/rest/v3/domains", headers=headers, cert="/home/vladislav/x-cmdbuild.crt")

    # domains
    def get_domains_list(self):
        pass

    # domain attributes
    def get_attributes_list(limit: int, start: int, *args, **kwargs):
        raise NotImplemented

    def get_attribute(self, attribute_id: str, *args, **kwargs):
        raise NotImplemented

    def create_attribute(self, data: Dict):
        raise NotImplemented
    
    def update_attibute(self, data: Dict):
        raise NotImplemented

    def delete_attibute(self, attribute_id: str):
        raise NotImplemented

    def reorder_attributes(self, order: List[str]):
        raise NotImplemented
