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
            f"'{value}' is not a valid {cls.__name__}. Expected one of {[member.value for member in cls]}"
        )


class SortDirection(_Enum):
    ASC = "asc"
    DESC = "desc"
