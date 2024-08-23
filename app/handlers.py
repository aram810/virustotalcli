import contextlib
import datetime
import pathlib
from collections.abc import Awaitable, Callable, Sequence

import httpx
import structlog

from app import io, transformers
from app.api import client, models

_logger = structlog.get_logger(__name__)


async def _make_orchestrator(
    api_key: str,
    stack: contextlib.AsyncExitStack,
    group_max_size: int,
) -> client.VirusTotalClientOrchestrator:
    return client.VirusTotalClientOrchestrator(
        client=client.VirusTotalClient(
            http_client=await stack.enter_async_context(
                httpx.AsyncClient(
                    http2=True,
                ),
            ),
            api_key=api_key,
        ),
        group_max_size=group_max_size,
    )


async def _read_ids(source: pathlib.Path) -> list[str] | None:
    try:
        return await io.read_ips(source)
    except io.InvalidSourceContentError:
        _logger.exception("Invalid source content")

        return None
    except IOError:
        _logger.exception("Failed to open the file")

        return None


async def _lookup_handler(
    source: pathlib.Path,
    reader: Callable[[pathlib.Path], Awaitable[list[str] | None]],
    lookuper: Callable[[Sequence[str]], Awaitable[list[models.LookupResponse]]],
) -> None:
    ids = await reader(source)

    if ids is None:
        return

    responses = await lookuper(ids)

    if not responses:
        _logger.info("No successful results")

        return

    lookup_results = transformers.lookups_to_results(responses)

    try:
        await io.write_analysis_results(
            output_path=pathlib.Path(
                "{0}.json".format(datetime.datetime.now().isoformat())
            ),
            results=lookup_results,
        )
    except IOError:
        _logger.exception("Failed to write into the file")

        return
    else:
        _logger.info(
            "Successfully inspected IDs: {}".format(
                ", ".join([res.identifier for res in lookup_results.results])
            )
        )


async def url_lookup_handler(
    source: pathlib.Path,
    api_key: str,
    group_max_size: int,
) -> None:
    async with contextlib.AsyncExitStack() as stack:
        api_orchestrator = await _make_orchestrator(api_key, stack, group_max_size)

        await _lookup_handler(
            source=source,
            reader=io.read_urls,
            lookuper=api_orchestrator.lookup_urls,
        )


async def ip_lookup_handler(
    source: pathlib.Path,
    api_key: str,
    group_max_size: int,
) -> None:
    async with contextlib.AsyncExitStack() as stack:
        api_orchestrator = await _make_orchestrator(api_key, stack, group_max_size)

        await _lookup_handler(
            source=source,
            reader=io.read_ips,
            lookuper=api_orchestrator.lookup_ips,
        )
