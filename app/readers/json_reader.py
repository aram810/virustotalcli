import json
import pathlib

import aiofiles

from app import managers
from app.readers import errors, filters


class JsonFileReader(managers.IdentifierReader):
    def __init__(
        self,
        source: pathlib.Path,
        filter_: filters.IdentifiersFilter,
    ) -> None:
        self._source = source
        self._filter = filter_

    async def read(self) -> list[str]:
        try:
            async with aiofiles.open(self._source) as file:
                identifiers = json.loads(await file.read())
        except json.JSONDecodeError as ex:
            raise errors.InvalidInputContentError from ex

        if not identifiers or not isinstance(identifiers, list):
            raise errors.InvalidInputContentError(
                "Input file must contain a non-empty array"
            )

        return self._filter.filter(identifiers)
