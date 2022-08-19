import enum as _enum


class _Enum(str, _enum.Enum):
    """
    An `enum.Enum` subclass that enables string comparison (`Enum.MEMBER == "MEMBER"`) and better exceptions that show
    all possible values.
    """

    @classmethod
    def _missing_(cls, value):
        if value in cls.__members__:
            return None
        raise ValueError(
            f"'{value}' is not a valid {cls.__module__}.{cls.__name__}. Expected one of {list(cls)}"
        )

    def __iter__(self):
        return iter(self.__members__)


class SrtDir(_Enum):
    ASC = "asc"
    DESC = "desc"
