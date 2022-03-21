
import argparse
from typing import Dict
from requests import Session, Response


def generate_session_token(session, args) -> str:

    """
        Every request requires the user to specify in the header the field “Cmdbuild-authorization”, that
        field is a session token generated when creating a session.
        method: post
        url: http://hostname:port/cmdbuild/services/rest/v3/sessions?scope=service&returnId=true
    """

    headers: Dict = {
        'Content-Type': 'application/json'
    }
    auth: Dict = {
        "username": args.username,
        "password": args.password,
    }
    url: str = f"https://{args.ip_address}/ready2use-2.2-3.4/services/rest/v3/sessions?scope=service&returnId=true"
    response: Response = session.post(
        url,
        headers=headers,
        verify=args.cert_path,
        json=auth
    )

    response.raise_for_status()
    responce_payload: Dict = response.json()
    token: str = responce_payload['data']['_id']
    return token

if __name__ == '__main__':

    """
        Example:
        python3 -m scripts --ip_address '127.0.0.1' --user 'admin' --pass 'admin' --cert_path '/home/vladislav/x-cmdbuild.key'
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_address', dest='ip_address', type=str, required=True)
    parser.add_argument('--user', dest='username', type=str, required=True)
    parser.add_argument('--pass', dest='password', type=str, required=True)
    parser.add_argument('--cert_path', dest='cert_path', type=str, required=True)
    args = parser.parse_args()

    session: Session = Session()
    token: str = generate_session_token(session, args)
    