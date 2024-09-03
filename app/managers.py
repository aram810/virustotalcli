import abc
from collections.abc import Sequence

from app.api import models as api_models


class MultipleResourceLookuper(abc.ABC):
    @abc.abstractmethod
    async def lookup(
        self,
        identifiers: Sequence[str],
    ) -> list[api_models.LookupResponse]:
        pass


class IdentifierReader(abc.ABC):
    @abc.abstractmethod
    async def read(self) -> list[str]:
        pass


class ResultsPresenter(abc.ABC):
    @abc.abstractmethod
    async def present(self, results: list[api_models.LookupResponse]) -> None:
        pass


class LookupManager:
    def __init__(
        self,
        reader: IdentifierReader,
        presenter: ResultsPresenter,
        lookuper: MultipleResourceLookuper,
    ) -> None:
        self._reader = reader
        self._presenter = presenter
        self._lookuper = lookuper

    async def present_lookup_results(self) -> None:
        identifiers = await self._reader.read()
        lookup_results = await self._lookuper.lookup(identifiers)
        await self._presenter.present(lookup_results)
