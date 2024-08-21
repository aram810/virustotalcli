import datetime
from collections.abc import Sequence

import pydantic
from pydantic import alias_generators


class AnalysisResult(pydantic.BaseModel):
    identifier: str
    type: str
    last_analysis_time: datetime.datetime
    is_malicious: bool

    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.AliasGenerator(
            serialization_alias=alias_generators.to_pascal,
        )
    )


class AnalysisResults(pydantic.BaseModel):
    results: Sequence[AnalysisResult]
