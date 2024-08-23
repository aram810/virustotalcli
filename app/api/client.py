import asyncio
import base64
from collections.abc import Awaitable, Callable, Sequence
from typing import cast

import httpx
import structlog

from app.api import models


class VirusTotalClient:
    _ip_lookup_endpoint_template: str = (
        "https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    )
    _url_lookup_endpoint_template: str = "https://www.virustotal.com/api/v3/urls/{url}"

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

    async def lookup_ip(self, ip: str) -> models.LookupResponse:
        response = await self._client.get(
            url=self._ip_lookup_endpoint_template.format(ip=ip),
            headers=self._default_headers,
        )

        response.raise_for_status()

        return models.LookupResponse(**response.json())

    async def lookup_url(self, url: str) -> models.LookupResponse:
        response = await self._client.get(
            url=self._url_lookup_endpoint_template.format(
                url=base64.b64encode(url.encode()).decode()
            ),
            headers=self._default_headers,
        )

        response.raise_for_status()

        return models.LookupResponse(**response.json())


class VirusTotalClientOrchestrator:
    def __init__(self, client: VirusTotalClient, group_max_size: int) -> None:
        self._client = client
        self._group_max_size = group_max_size
        self._logger = structlog.get_logger(__name__)

    async def lookup_ips(self, ips: Sequence[str]) -> list[models.LookupResponse]:
        return await self._lookup(ips, self._client.lookup_ip)

    async def lookup_urls(self, urls: Sequence[str]) -> list[models.LookupResponse]:
        return await self._lookup(urls, self._client.lookup_url)

    async def _lookup(
        self,
        identifiers: Sequence[str],
        lookup_func: Callable[[str], Awaitable[models.LookupResponse]],
    ) -> list[models.LookupResponse]:
        responses = []

        for i in range(0, len(identifiers), self._group_max_size):
            tasks = [
                lookup_func(url) for url in identifiers[i : i + self._group_max_size]
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
