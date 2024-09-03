from app import managers
from app.api import models


def _is_malicious(stats: models.LastAnalysisStats) -> bool:
    return stats.malicious + stats.suspicious > stats.harmless


class CliPresenter(managers.ResultsPresenter):
    async def present(self, results: list[models.LookupResponse]) -> None:
        for resp in results:
            print(
                "{0} is {1}".format(
                    resp.data.identifier,
                    "malicious"
                    if _is_malicious(resp.data.attributes.last_analysis_stats)
                    else "safe",
                )
            )
