import abc

import validators


class Validator(abc.ABC):
    @abc.abstractmethod
    def validate(self, identifier: str) -> None:
        pass


class IpValidator(Validator):
    def validate(self, identifier: str) -> None:
        try:
            validators.ipv6(identifier, r_ve=True)
        except validators.ValidationError:
            try:
                validators.ipv4(identifier, r_ve=True)
            except validators.ValidationError as ex:
                raise ValueError from ex


class UrlValidator(Validator):
    def validate(self, identifier: str) -> None:
        try:
            validators.url(
                identifier, skip_ipv4_addr=True, skip_ipv6_addr=True, r_ve=True
            )
        except validators.ValidationError as ex:
            raise ValueError from ex
