import datetime
from collections.abc import Sequence

import aiofiles
import pydantic
from pydantic import alias_generators

from app import managers
from app.api import models


class _AnalysisResult(pydantic.BaseModel):
    identifier: str
    type: str
    last_analysis_time: datetime.datetime
    is_malicious: bool

    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.AliasGenerator(
            serialization_alias=alias_generators.to_pascal,
        )
    )


class _AnalysisResults(pydantic.BaseModel):
    results: Sequence[_AnalysisResult]


def _is_malicious(stats: models.LastAnalysisStats) -> bool:
    return stats.malicious + stats.suspicious > stats.harmless


def _lookups_to_results(
    responses: Sequence[models.LookupResponse],
) -> _AnalysisResults:
    return _AnalysisResults(
        results=[
            _AnalysisResult(
                identifier=response.data.identifier,
                type=response.data.type.upper(),
                last_analysis_time=response.data.attributes.last_analysis_date,
                is_malicious=_is_malicious(
                    response.data.attributes.last_analysis_stats
                ),
            )
            for response in responses
        ],
    )


def _analysis_results_to_json(analysis_results: _AnalysisResults) -> str:
    return analysis_results.model_dump_json(indent=4, by_alias=True)


class JsonFilePresenter(managers.ResultsPresenter):
    async def present(self, results: list[models.LookupResponse]) -> None:
        async with aiofiles.open(
            "{0}.json".format(datetime.datetime.now().isoformat()), "w"
        ) as file:
            await file.write(
                _analysis_results_to_json(
                    _lookups_to_results(results),
                ),
            )
