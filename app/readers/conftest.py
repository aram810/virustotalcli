import pytest

from app.readers import json_reader, validator


@pytest.fixture()
def ip_validator() -> validator.Validator:
    return json_reader.IpValidator()


@pytest.fixture()
def url_validator() -> validator.Validator:
    return json_reader.UrlValidator()
