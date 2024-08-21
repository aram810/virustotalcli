from typing import Any

import validators


def validate_ip_address(ip: Any) -> None:
    try:
        validators.ipv6(ip, r_ve=True)
    except validators.ValidationError:
        try:
            validators.ipv4(ip, r_ve=True)
        except validators.ValidationError as ex:
            raise ValueError from ex


def validate_url(url: str) -> None:
    try:
        validators.url(url, skip_ipv4_addr=True, skip_ipv6_addr=True, r_ve=True)
    except validators.ValidationError as ex:
        raise ValueError from ex
