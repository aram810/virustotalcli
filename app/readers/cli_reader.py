from app import managers
from app.readers import errors, filters


class CliReader(managers.IdentifierReader):
    def __init__(
        self,
        filter_: filters.IdentifiersFilter,
    ) -> None:
        self._filter = filter_

    async def read(self) -> list[str]:
        identifiers = input("Please input comma-separated identifiers: ").strip()

        if not identifiers:
            raise errors.InvalidInputContentError("Input can't be empty")

        identifiers_list = [id_.strip() for id_ in identifiers.split(",")]

        return self._filter.filter(identifiers_list)
