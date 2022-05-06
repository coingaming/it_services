import json
import logging
from typing import Dict
from pathlib import Path, PosixPath
from fastapi import FastAPI, Request, Response
from .utils import EmployeeInitialContext, verify_signature, load_config


PROJECT_ROOT: PosixPath = Path(__file__).parent.parent
APP_NAME = "hibob-webhook-listener"

app = FastAPI(
    title="Hibob Webhook Listener",
    description="",
    version="1.0",
)

WEBHOOK_SECRET: str = ""  # test api key
BOB_ACCESS_TOKEN: str = ""


logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
file_logging = logging.FileHandler(f"{APP_NAME}.log")
file_logging.setFormatter(formatter)
logger.addHandler(file_logging)


@app.on_event("startup")
async def startup_event():
    """
    During the startup of the app:
    1. merge employee info from hr system and cmdbuild
    2. apply all the differences between 2 systems
    3. todo: memcache provisioning
    """
    # 1. request all employee info from hibob
    config: Dict = load_config(PROJECT_ROOT / "configs" / "base.yml")
    cmdbuild_config: Dict = config["cmdbuild"]
    hr_system_config: Dict = config["hr_system"]

    cmdbuild_url: str = cmdbuild_config["url"]["debug"]
    hr_system_url: str = hr_system_config["url"]["debug"]
    if not config["debug"]:
        cmdbuild_url = config["cmdbuild"]["prod"]
        hr_system_url = config["hr_system"]["prod"]

    employee_ctx: EmployeeInitialContext = EmployeeInitialContext(
        bob_token=BOB_ACCESS_TOKEN,
        username_cmdbuild="",
        password_cmdbuild="",
        cmdbuild_url=cmdbuild_url,
        bob_url=hr_system_url,
    )
    await employee_ctx.prepare()


@app.post("/webhook/")
async def webhook(request: Request, response: Response):

    bob_signature: bytes = request.headers.get("bob-signature")
    # content_length: int = int(request.headers.get('content-length')) 
    # todo check content length to avoid memory allocation attacks

    body: bytes = await request.body()
    result: bool = verify_signature(bob_signature, body)
    if not result:
        logger.error("Invalid message signature")
        response.status_code = 400
        return
    data: Dict = json.loads(body)
