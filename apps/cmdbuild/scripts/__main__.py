import sys
from logging import Logger, getLogger, Formatter, StreamHandler, DEBUG, INFO
import argparse
from requests import Session
from scripts.version_updaters import update_version
from scripts.web_clients.cmdbuild import CmdBuildWebClient

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

    logger: Logger = getLogger()
    logger.setLevel(INFO)
    handler: StreamHandler = StreamHandler(sys.stdout)
    handler.setLevel(DEBUG)
    formatter: Formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    session: Session = Session()
    session.verify = args.cert_path

    base_url: str = f"https://{args.ip_address}/ready2use-2.2-3.4/services"
    cmdbuild_client: CmdBuildWebClient = CmdBuildWebClient(
        session=session,
        base_url=base_url,
        logger=logger
    )
    cmdbuild_client.path = "rest/v3/sessions?scope=service&returnId=true"
    cmdbuild_client.generate_session_token(args.username, args.password)

    update_version(cmdbuild_client, logger)