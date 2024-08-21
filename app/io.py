import json
import pathlib
from collections.abc import Callable

import aiofiles
import structlog

from app import models, validator_wrappers

_logger = structlog.get_logger(__name__)


class InvalidSourceContentError(Exception):
    """Raised when source content in invalid."""


async def read_ips(source: pathlib.Path) -> list[str]:
    return await _read_ids(source, validator_wrappers.validate_ip_address, "IP address")


async def read_urls(source: pathlib.Path) -> list[str]:
    return await _read_ids(source, validator_wrappers.validate_url, "URL")


async def _read_ids(
    source: pathlib.Path, validator: Callable[[str], None], id_type: str
) -> list[str]:
    try:
        async with aiofiles.open(source) as file:
            ids = json.loads(await file.read())
    except json.JSONDecodeError as ex:
        raise InvalidSourceContentError from ex

    valid_ids = []

    for identifier in ids:
        try:
            validator(identifier)
        except ValueError:
            _logger.exception(
                "Input file contains invalid {0}".format(id_type), identifier=identifier
            )
        else:
            valid_ids.append(identifier)

    return valid_ids


async def write_analysis_results(
    output_path: pathlib.Path, results: models.AnalysisResults
) -> None:
    async with aiofiles.open(output_path, "w") as file:
        await file.write(results.model_dump_json(indent=4))
