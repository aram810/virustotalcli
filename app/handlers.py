import asyncio
import contextlib
import pathlib
from collections.abc import Coroutine

import httpx
import structlog

from app import managers
from app.api import client
from app.presenters import json_presenter
from app.readers import filters, json_reader

_logger = structlog.get_logger(__name__)


def run_loop_handle_exceptions(main: Coroutine[None, None, None], debug: bool) -> None:
    try:
        asyncio.run(
            main=main,
            debug=debug,
        )
    except Exception as ex:
        _logger.exception(
            "An unhandled exception occurred",
        )
        raise SystemExit(1) from ex


async def ip_lookup_handler(
    source: pathlib.Path,
    api_key: str,
    group_max_size: int,
) -> None:
    async with contextlib.AsyncExitStack() as stack:
        await managers.LookupManager(
            reader=json_reader.JsonFileReader(
                source=source,
                filter_=filters.IdentifiersFilter(
                    validator=json_reader.IpValidator(),
                ),
            ),
            presenter=json_presenter.JsonFilePresenter(),
            lookuper=client.VirusTotalClientOrchestrator(
                client=client.VirusTotalIpLookupClient(
                    http_client=await stack.enter_async_context(
                        httpx.AsyncClient(
                            http2=True,
                        ),
                    ),
                    api_key=api_key,
                ),
                group_max_size=group_max_size,
            ),
        ).present_lookup_results()


async def url_lookup_handler(
    source: pathlib.Path,
    api_key: str,
    group_max_size: int,
) -> None:
    async with contextlib.AsyncExitStack() as stack:
        await managers.LookupManager(
            reader=json_reader.JsonFileReader(
                source=source,
                filter_=filters.IdentifiersFilter(
                    validator=json_reader.UrlValidator(),
                ),
            ),
            presenter=json_presenter.JsonFilePresenter(),
            lookuper=client.VirusTotalClientOrchestrator(
                client=client.VirusTotalUrlLookupClient(
                    http_client=await stack.enter_async_context(
                        httpx.AsyncClient(
                            http2=True,
                        ),
                    ),
                    api_key=api_key,
                ),
                group_max_size=group_max_size,
            ),
        ).present_lookup_results()
