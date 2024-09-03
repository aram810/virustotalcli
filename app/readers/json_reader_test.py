import pytest

from app.readers import validator

_VALID_IP = "127.0.0.1"
_INVALID_IP = "blabla"

_VALID_URL = "https://facebook.com"
_INVALID_URL = ".facebook.com"


def test_validate_ip(ip_validator: validator.Validator) -> None:
    ip_validator.validate(_VALID_IP)

    with pytest.raises(ValueError):
        ip_validator.validate(_INVALID_IP)


def test_validate_url(url_validator: validator.Validator) -> None:
    url_validator.validate(_VALID_URL)

    with pytest.raises(ValueError):
        url_validator.validate(_INVALID_URL)
