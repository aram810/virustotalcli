import json
from collections.abc import AsyncIterator
from typing import Any

import aiofiles
import httpx
import pytest

from app.api import client


async def load_json_fixture(
    file_path: str,
) -> dict[str, Any]:
    async with aiofiles.open(file_path) as file_handle:
        return json.loads(await file_handle.read())


@pytest.fixture()
async def http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as http_client:
        yield http_client


@pytest.fixture()
def api_client(http_client: httpx.AsyncClient) -> client.VirusTotalClient:
    return client.VirusTotalClient(
        http_client=http_client,
        api_key="",
    )


@pytest.fixture()
def orchestrator(
    api_client: client.VirusTotalClient,
) -> client.VirusTotalClientOrchestrator:
    return client.VirusTotalClientOrchestrator(
        client=api_client,
    )
