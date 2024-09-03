import json
import pathlib

import aiofiles
import validators

from app import managers
from app.readers import errors, filters, validator


class IpValidator(validator.Validator):
    def validate(self, identifier: str) -> None:
        try:
            validators.ipv6(identifier, r_ve=True)
        except validators.ValidationError:
            try:
                validators.ipv4(identifier, r_ve=True)
            except validators.ValidationError as ex:
                raise ValueError from ex


class UrlValidator(validator.Validator):
    def validate(self, identifier: str) -> None:
        try:
            validators.url(
                identifier, skip_ipv4_addr=True, skip_ipv6_addr=True, r_ve=True
            )
        except validators.ValidationError as ex:
            raise ValueError from ex


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
