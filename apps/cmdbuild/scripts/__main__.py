import sys
from logging import Logger, getLogger, Formatter, StreamHandler, DEBUG, INFO
import argparse
from requests import Session
from scripts.version_updaters import update_version
from scripts.web_clients.cmdbuild import CmdBuildWebClient
from scripts.web_clients.hibob import HiBobWebClient


if __name__ == '__main__':

    """
        Example:
        python3 -m scripts \
            --ip_cmdbuild '127.0.0.1' \
            --user_cmdbuild 'admin' \
            --pass_cmdbuild 'admin' \
            --cert_path_cmdbuild '~./x-cmdbuild.crt' \
            --url_hibob 'https://api.hibob.com/v1/people?showInactive=false&includeHumanReadable=true',
            --token_hibob '6RnF2ZjVjV'
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_cmdbuild', dest='ip_cmdbuild', type=str, required=True)
    parser.add_argument('--user_cmdbuild', dest='user_cmdbuild', type=str, required=True)
    parser.add_argument('--pass_cmdbuild', dest='pass_cmdbuild', type=str, required=True)
    parser.add_argument('--url_hibob', dest='url_hibob', type=str, required=True)
    parser.add_argument('--token_hibob', dest='token_hibob', type=str, required=True)
    parser.add_argument('--cert_path_cmdbuild', dest='cert_path_cmdbuild', type=str)

    args = parser.parse_args()
    logger: Logger = getLogger()
    logger.setLevel(INFO)
    handler: StreamHandler = StreamHandler(sys.stdout)
    handler.setLevel(DEBUG)
    formatter: Formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    verify=args.cert_path_cmdbuild is not None
    session: Session = Session()
    if verify:
        session.verify = args.cert_path_cmdbuild
    base_url: str = f"https://{args.ip_cmdbuild}/ready2use-2.2-3.4/services"
    cmdbuild_client: CmdBuildWebClient = CmdBuildWebClient(
        session=session,
        base_url=base_url,
        verify=verify,
        logger=logger
    )
    cmdbuild_client.path = "rest/v3/sessions?scope=service&returnId=true"
    cmdbuild_client.generate_session_token(args.user_cmdbuild, args.pass_cmdbuild)
    hibob_client: HiBobWebClient = HiBobWebClient(url=args.url_hibob, token=args.token_hibob)
    update_version(hibob_client, cmdbuild_client, logger)