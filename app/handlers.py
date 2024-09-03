import asyncio
import contextlib
import pathlib
import types
from collections.abc import Coroutine

import httpx
import structlog

from app import managers
from app.api import client
from app.presenters import cli_presenter, json_presenter
from app.readers import cli_reader, filters, json_reader, validator

_logger = structlog.get_logger(__name__)

_READER_MAP = types.MappingProxyType(
    {
        "json-file": json_reader.JsonFileReader,
        "cli": cli_reader.CliReader,
    },
)
_PRESENTER_MAP = types.MappingProxyType(
    {
        "json-file": json_presenter.JsonFilePresenter,
        "cli": cli_presenter.CliPresenter,
    },
)


def _reader_factory(reader_type: str, **kwargs) -> managers.IdentifierReader:
    kwargs = {key_: val for key_, val in kwargs.items() if val is not None}

    return _READER_MAP[reader_type](**kwargs)


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
    api_key: str,
    group_max_size: int,
    reader: str,
    presenter: str,
    source: pathlib.Path | None,
) -> None:
    async with contextlib.AsyncExitStack() as stack:
        await managers.LookupManager(
            reader=_reader_factory(
                reader_type=reader,
                source=source,
                filter_=filters.IdentifiersFilter(
                    validator=validator.IpValidator(),
                ),
            ),
            presenter=_PRESENTER_MAP[presenter](),
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
    api_key: str,
    group_max_size: int,
    reader: str,
    presenter: str,
    source: pathlib.Path | None,
) -> None:
    async with contextlib.AsyncExitStack() as stack:
        await managers.LookupManager(
            reader=_reader_factory(
                reader_type=reader,
                source=source,
                filter_=filters.IdentifiersFilter(
                    validator=validator.UrlValidator(),
                ),
            ),
            presenter=_PRESENTER_MAP[presenter](),
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
