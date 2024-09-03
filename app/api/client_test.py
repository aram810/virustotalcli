import logging

import httpx
import pytest
import pytest_httpx

from app import conftest, logger
from app.api import client, models

logger.configure_logger(False)


async def test_stat_is_readable(
    httpx_mock: pytest_httpx.HTTPXMock,
    url_lookup_client: client.VirusTotalClient,
) -> None:
    httpx_mock.add_response(
        url="https://www.virustotal.com/api/v3/urls/ZmIuY29t",
        status_code=200,
        json=await conftest.load_json_fixture("app/api/fixtures/good_url_lookup.json"),
    )

    response = await url_lookup_client.lookup("fb.com")

    assert isinstance(response, models.LookupResponse)
    assert isinstance(
        response.data.attributes.last_analysis_stats, models.LastAnalysisStats
    )
    assert response.data.attributes.last_analysis_stats.harmless == 70


async def test_error_response_raises(
    httpx_mock: pytest_httpx.HTTPXMock,
    url_lookup_client: client.VirusTotalClient,
) -> None:
    httpx_mock.add_response(
        url="https://www.virustotal.com/api/v3/urls/ZmIuY29t",
        status_code=401,
    )

    with pytest.raises(httpx.HTTPError):
        await url_lookup_client.lookup("fb.com")


async def test_orchestrator_logs_on_failure(
    httpx_mock: pytest_httpx.HTTPXMock,
    caplog: pytest.LogCaptureFixture,
    url_lookup_orchestrator: client.VirusTotalClientOrchestrator,
) -> None:
    httpx_mock.add_response(
        url="https://www.virustotal.com/api/v3/urls/ZmIuY29t",
        status_code=401,
    )

    with caplog.at_level(logging.INFO):
        await url_lookup_orchestrator.lookup(
            [
                "fb.com",
            ]
        )

    assert "Lookup failed" in caplog.text
