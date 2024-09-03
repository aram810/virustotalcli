import datetime
import json

from app import conftest
from app.api import models
from app.presenters import json_presenter

_LOOKUP_RESULTS = [
    models.LookupResponse(
        data=models.LookupData(
            id="127.0.0.1",
            type="ip_address",
            attributes=models.LookupAttributes(
                last_analysis_stats=models.LastAnalysisStats(
                    harmless=10,
                    malicious=5,
                    suspicious=2,
                    timeout=0,
                    undetected=0,
                ),
                last_analysis_date=datetime.datetime(
                    year=2024,
                    month=8,
                    day=22,
                    hour=13,
                    minute=25,
                    second=8,
                ),
            ),
        ),
    ),
    models.LookupResponse(
        data=models.LookupData(
            id="127.0.0.2",
            type="ip_address",
            attributes=models.LookupAttributes(
                last_analysis_stats=models.LastAnalysisStats(
                    harmless=10,
                    malicious=5,
                    suspicious=20,
                    timeout=0,
                    undetected=0,
                ),
                last_analysis_date=datetime.datetime(
                    year=2024,
                    month=8,
                    day=22,
                    hour=15,
                    minute=38,
                    second=44,
                ),
            ),
        ),
    ),
]
_EXPECTED_ANALYSIS_RESULTS = json_presenter._AnalysisResults(
    results=[
        json_presenter._AnalysisResult(
            identifier="127.0.0.1",
            type="IP_ADDRESS",
            last_analysis_time=datetime.datetime(
                year=2024,
                month=8,
                day=22,
                hour=13,
                minute=25,
                second=8,
            ),
            is_malicious=False,
        ),
        json_presenter._AnalysisResult(
            identifier="127.0.0.2",
            type="IP_ADDRESS",
            last_analysis_time=datetime.datetime(
                year=2024,
                month=8,
                day=22,
                hour=15,
                minute=38,
                second=44,
            ),
            is_malicious=True,
        ),
    ]
)


def test_lookup_results_to_analysis_results():
    assert _EXPECTED_ANALYSIS_RESULTS == json_presenter._lookups_to_results(
        _LOOKUP_RESULTS
    )


async def test_output_json():
    expected_json = await conftest.load_json_fixture(
        "app/presenters/fixtures/localhost_lookup_results.json"
    )
    converted_json = json_presenter._analysis_results_to_json(
        json_presenter._lookups_to_results(_LOOKUP_RESULTS)
    )

    assert expected_json == json.loads(converted_json)
