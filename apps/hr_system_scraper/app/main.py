import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict
from pathlib import Path, PosixPath
import httpx
from fastapi import FastAPI, Request, Response
from .utils import (
    EmployeeInterSystemsContext,
    verify_signature,
    get_base_url,
    load_config,
)


PROJECT_ROOT: PosixPath = Path(__file__).parent.parent
APP_NAME = "hibob-webhook-listener"
app = FastAPI(title="Hibob Webhook Listener", description="", version="1.0")
logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s")
ts = datetime.utcfromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
file_logging = logging.FileHandler(f"{APP_NAME}-{ts}.log")
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
    config: Dict = load_config(PROJECT_ROOT / "configs" / "base.yml")
    employee_ctx: EmployeeInterSystemsContext = None
    async with (
        httpx.AsyncClient(
            base_url=get_base_url(config, "cmdbuild"), verify=False
        ) as cmdbuild_http_client,
        httpx.AsyncClient(
            base_url=get_base_url(config, "hr_system")
        ) as bob_http_client,
    ):
        try:
            employee_ctx = EmployeeInterSystemsContext(
                bob_http_client, cmdbuild_http_client, logger
            )
            await employee_ctx.prepare()
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP Exception for {exc.request.url} - {exc}")
        finally:
            if employee_ctx is not None:
                employee_ctx.clear()

async def on_employee_created(hook_payload: Dict, response: Response):
    config: Dict = load_config(PROJECT_ROOT / "configs" / "base.yml")
    employee_ctx: EmployeeInterSystemsContext = None
    employee_id: str = hook_payload["employee"]["id"]
    async with (
        httpx.AsyncClient(
            base_url=get_base_url(config, "cmdbuild"), verify=False
        ) as cmdbuild_http_client,
        httpx.AsyncClient(
            base_url=get_base_url(config, "hr_system")
        ) as bob_http_client,
    ):
        try:
            employee_ctx = EmployeeInterSystemsContext(
                bob_http_client, cmdbuild_http_client, logger
            )
            await employee_ctx.create_cmdb_employee(employee_id)
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP Exception for {exc.request.url} - {exc}")
        finally:
            if employee_ctx is not None:
                employee_ctx.clear()

async def on_employee_updated(hook_payload: Dict, response: Response):
    employee_id: str = hook_payload["employee"]["id"]
    field_updates: Dict = hook_payload["data"]["fieldUpdates"]
    cmdbuild_http_client = httpx.AsyncClient(verify=False)
    bob_http_client = httpx.AsyncClient()
    try:
        employee_ctx: EmployeeInterSystemsContext = EmployeeInterSystemsContext(
            bob_http_client, cmdbuild_http_client, logger
        )
        await employee_ctx.update_cmdb_employee(employee_id, field_updates)
    except (httpx.HTTPStatusError, AssertionError) as err:
        display_name: str = hook_payload["employee"]["displayName"]
        logger.exception("Failed to create employee %s err %s", display_name, str(err))
        response.status_code = 500
    finally:
        employee_ctx.clear()
        await asyncio.gather(cmdbuild_http_client.aclose(), bob_http_client.aclose())


@app.post("/webhook/")
async def webhook(request: Request, response: Response):
    bob_signature: bytes = request.headers.get("bob-signature")
    body: bytes = await request.body()
    result: bool = verify_signature(bob_signature, body)
    if result:
        hook_payload: Dict = json.loads(body)
        event_type: str = hook_payload["type"]
        match hook_payload["type"]:
            case "employee.created":
                await on_employee_created(hook_payload, response)
            case _:
                logger.warning(
                    "Unknown event type %s with payload %s", event_type, hook_payload
                )
    else:
        logger.error("Invalid message signature")
        response.status_code = 400
