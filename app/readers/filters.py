from collections.abc import Sequence

import structlog

from app.readers import errors
from app.readers import validator as validator_module


class IdentifiersFilter:
    def __init__(self, validator: validator_module.Validator) -> None:
        self._validator = validator
        self._logger = structlog.get_logger(__name__)

    def filter(self, identifiers: Sequence[str]) -> list[str]:
        valid_ids = []

        for idf in identifiers:
            try:
                self._validator.validate(idf)
            except ValueError:
                self._logger.warning("Invalid identifier {0}".format(idf))
            else:
                valid_ids.append(idf)

        if not valid_ids:
            raise errors.InvalidInputContentError(
                "No valid identifier found in the input file"
            )

        return valid_ids
