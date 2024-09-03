import logging

import pytest

from app import logger
from app.readers import errors, filters, validator

_VALID_IP = "127.0.0.1"
_INVALID_IP = "127.0.0.1.1"


logger.configure_logger(False)


@pytest.fixture()
def ip_filter(ip_validator: validator.Validator) -> filters.IdentifiersFilter:
    return filters.IdentifiersFilter(ip_validator)


def test_filter_some_ids(
    ip_filter: filters.IdentifiersFilter,
    caplog: pytest.LogCaptureFixture,
) -> None:
    identifiers = [_VALID_IP, _INVALID_IP]

    with caplog.at_level(logging.WARNING):
        assert ip_filter.filter(identifiers) == [_VALID_IP]

    assert "Invalid identifier 127.0.0.1.1" in caplog.text


def test_filter_all_ids(ip_filter: filters.IdentifiersFilter) -> None:
    identifiers = [_INVALID_IP, _INVALID_IP]

    with pytest.raises(errors.InvalidInputContentError):
        ip_filter.filter(identifiers)
