import pytest

from app.readers import validator


@pytest.fixture()
def ip_validator() -> validator.Validator:
    return validator.IpValidator()


@pytest.fixture()
def url_validator() -> validator.Validator:
    return validator.UrlValidator()
