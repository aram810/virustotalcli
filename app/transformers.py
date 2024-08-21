from collections.abc import Sequence

from app import models
from app.api import models as api_models


def _is_malicious(stats: api_models.LastAnalysisStats) -> bool:
    return stats.malicious + stats.suspicious > stats.harmless


def lookups_to_results(
    responses: Sequence[api_models.LookupResponse],
) -> models.AnalysisResults:
    return models.AnalysisResults(
        results=[
            models.AnalysisResult(
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
