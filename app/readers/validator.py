import abc


class Validator(abc.ABC):
    @abc.abstractmethod
    def validate(self, identifier: str) -> None:
        pass
