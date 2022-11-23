from __future__ import annotations

from csv import DictReader
from datetime import datetime
from datetime import timedelta
from json import JSONDecodeError

import requests
from boltons.jsonutils import JSONLIterator
from pydantic import BaseModel
from pydantic import PrivateAttr
from pydantic import root_validator
from pydantic import SecretStr
from pydantic import ValidationError


class Model(BaseModel):
    """
    Subclass of pydantic's `BaseModel` to change the `.dict()` and `.json()` methods to dump fields with `by_alias=True`
    as the default.
    """

    def json(
        self,
        *,
        include=None,
        exclude=None,
        by_alias=True,
        skip_defaults=None,
        exclude_unset=False,
        exclude_defaults=False,
        exclude_none=False,
        encoder=None,
        models_as_dict=True,
        **dumps_kwargs,
    ):
        """
        Generate a JSON representation of the model, optionally specifying which fields to include or exclude.

        See [Pydantic docs](https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeljson) for full details.
        """
        return super().json(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            models_as_dict=models_as_dict,
            **dumps_kwargs,
        )

    def dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias=True,
        skip_defaults=None,
        exclude_unset=False,
        exclude_defaults=False,
        exclude_none=False,
    ):
        """
        Generate a dict representation of the model, optionally specifying which fields to include or exclude.

        See [Pydantic docs](https://pydantic-docs.helpmanual.io/usage/exporting_models/#modeldict) for full details.
        """
        return super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    @classmethod
    def parse_json_lines(cls, file):
        """
        Accepts an open file-like object in [JSON Lines format](https://jsonlines.org) and returns a generator of
        models parsed from the JSON line by line.
        """
        num = 1
        try:
            for line in JSONLIterator(file):
                try:
                    yield cls(**line)
                    num += 1
                except ValidationError as v_err:
                    raise ValueError(
                        f"Error parsing object on line {num}: {str(v_err)}"
                    )
        except JSONDecodeError:
            raise ValueError(
                f"Unable to parse line {num}. Expecting JSONLines format: https://jsonlines.org"
            )

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        json_encoders = {datetime: lambda dt: dt.isoformat().replace("+00:00", "Z")}
        extra = "allow"


class ResponseModel(Model):
    @classmethod
    def parse_response(cls, response: requests.Response):
        try:
            return cls.parse_raw(response.text)
        except ValidationError as err:
            err.response = response
            raise


class AuthResponse(ResponseModel):
    token_type: str
    expires_in: int
    access_token: SecretStr
    _init_time: datetime = PrivateAttr(default_factory=datetime.utcnow)

    @property
    def expired(self):
        return (datetime.utcnow() - self._init_time) > timedelta(
            seconds=self.expires_in
        )


class CSVModel(BaseModel, allow_population_by_field_name=True, extra="allow"):
    """
    Pydantic model class enables multiple aliases to be assigned to a single field value. If the field is required
    then at least one of the aliases must be supplied or validation will fail.

    Useful when parsing CSV data from multiple sources where the expected column header names might vary.

    For example, if a CSV requires a "user" column, which could either be a username or ID:

        class UserCSV(CSVModel):
            user: str = Field(csv_aliases=["user_id", "userId", "username"])
            department: Optional[str]

    Then a CSV could have any of the columns "username", "user_id", or "userId" and the "user" field will be populated
    with the value of that column.

    If a CSV file has multiple alias columns pointing to the same field (e.g. "username" and "userId"), the field will
    be populated by priority of the order of the `csv_aliases` list definition. So in the example above, a CSV that
    has both "username" and "userId" columns, the `model.user` field will be the "userId" CSV value. But because the
    model also allows extra values, "username" will still be accessible on the model at `model.username`.
    """

    @root_validator(pre=True)
    def _alias_validator(cls, values):  # noqa
        for name, field in cls.__fields__.items():
            aliases = field.field_info.extra.get("csv_aliases", [])
            for alias in aliases:
                if alias in values and values[alias]:
                    values[name] = values[alias]
                    break
            else:  # no break
                if field.required:
                    raise ValueError(
                        f"'{name}' required. Valid column aliases: {aliases}"
                    )

        return values

    @classmethod
    def parse_csv(cls, file):
        first_line = next(file)
        headers = first_line.strip().split(",")
        try:
            cls(**{key: "value" for key in headers})
        except ValidationError as err:
            msg = err.errors()[0]["msg"]
            raise ValueError(f"CSV header missing column: {msg}")

        reader = DictReader(file, fieldnames=headers, restkey="extra")
        for row in reader:
            try:
                # coerce empty columns from "" to None
                row = {k: v or None for k, v in row.items()}
                yield cls(**row)
            except ValidationError as err:
                msg = err.errors()[0]["msg"]
                raise ValueError(f"Missing data on CSV row {reader.line_num}: {msg}")
