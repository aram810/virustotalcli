import abc
import asyncio
import base64
from collections.abc import Sequence
from typing import cast

import httpx
import structlog

from app import managers
from app.api import models


class VirusTotalClient(abc.ABC):
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        api_key: str,
    ) -> None:
        self._client = http_client
        self._api_key = api_key

        self._default_headers = {
            "accept": "application/json",
            "x-apikey": self._api_key,
        }

    @abc.abstractmethod
    async def lookup(self, identifier: str) -> models.LookupResponse:
        pass


class VirusTotalIpLookupClient(VirusTotalClient):
    _ip_lookup_endpoint_template: str = (
        "https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    )

    async def lookup(self, identifier: str) -> models.LookupResponse:
        response = await self._client.get(
            url=self._ip_lookup_endpoint_template.format(ip=identifier),
            headers=self._default_headers,
        )

        response.raise_for_status()

        return models.LookupResponse(**response.json())


class VirusTotalUrlLookupClient(VirusTotalClient):
    _url_lookup_endpoint_template: str = "https://www.virustotal.com/api/v3/urls/{url}"

    async def lookup(self, identifier: str) -> models.LookupResponse:
        response = await self._client.get(
            url=self._url_lookup_endpoint_template.format(
                url=base64.b64encode(identifier.encode()).decode()
            ),
            headers=self._default_headers,
        )

        response.raise_for_status()

        return models.LookupResponse(**response.json())


class VirusTotalClientOrchestrator(managers.MultipleResourceLookuper):
    def __init__(self, client: VirusTotalClient, group_max_size: int) -> None:
        self._client = client
        self._group_max_size = group_max_size
        self._logger = structlog.get_logger(__name__)

    async def lookup(
        self,
        identifiers: Sequence[str],
    ) -> list[models.LookupResponse]:
        responses = []

        for i in range(0, len(identifiers), self._group_max_size):
            tasks = [
                self._client.lookup(url)
                for url in identifiers[i : i + self._group_max_size]
            ]

            group_responses = await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

            for response in group_responses:
                if isinstance(response, Exception):
                    self._logger.exception(
                        "Lookup failed",
                        exc_info=(
                            type(response),
                            response,
                            response.__traceback__,
                        ),
                    )
                    continue

                responses.append(response)

        return cast(list[models.LookupResponse], responses)
