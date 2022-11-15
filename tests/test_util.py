from typing import Optional

import pytest
from pydantic import BaseModel
from pydantic import Field

from incydr.utils import flatten_fields
from incydr.utils import get_field_value_and_info
from incydr.utils import get_fields
from incydr.utils import iter_model_formatted


class GrandChildTestModel(BaseModel):
    string_field: Optional[str] = Field(table=lambda x: str(x))


class ChildTestModel(BaseModel):
    string_field: Optional[str]
    int_field: Optional[int] = Field(
        table=lambda x: str(x + 1) if isinstance(x, int) else x,
        csv=lambda x: str(x + 2) if isinstance(x, int) else x,
    )
    grand_child: Optional[GrandChildTestModel]

    class Config:
        json_encoders = {int: lambda i: str(float(i))}


class ParentTestModel(BaseModel):
    string_field: Optional[str]
    int_field: Optional[int] = Field(
        table=lambda x: str(x + 1), csv=lambda x: str(x + 2)
    )
    child_model: Optional[ChildTestModel]

    class Config:
        json_encoders = {int: lambda i: str(float(i))}


def test_flatten():
    assert list(flatten_fields(ParentTestModel)) == [
        "string_field",
        "int_field",
        "child_model.string_field",
        "child_model.int_field",
        "child_model.grand_child.string_field",
    ]


def test_get_fields():
    assert list(get_fields(ParentTestModel)) == [
        "string_field",
        "int_field",
        "child_model",
    ]
    assert list(get_fields(ParentTestModel, flat=True)) == [
        "string_field",
        "int_field",
        "child_model.string_field",
        "child_model.int_field",
        "child_model.grand_child.string_field",
    ]
    assert list(get_fields(ParentTestModel, flat=True, include=["child_model.*"])) == [
        "child_model.string_field",
        "child_model.int_field",
        "child_model.grand_child.string_field",
    ]
    assert list(
        get_fields(ParentTestModel, flat=True, include=["child_model.*", "int_field"])
    ) == [
        "child_model.string_field",
        "child_model.int_field",
        "child_model.grand_child.string_field",
        "int_field",
    ]
    assert list(
        get_fields(
            ParentTestModel,
            flat=False,
            include=["child_model", "string_field", "int_field"],
        )
    ) == ["child_model", "string_field", "int_field"]

    with pytest.raises(ValueError) as err:
        list(get_fields(ParentTestModel, include=["not_valid"]))
    assert err.value.args[1] == ["string_field", "int_field", "child_model"]

    with pytest.raises(ValueError) as err2:
        list(get_fields(ParentTestModel, flat=True, include=["not_valid.*"]))
    assert err2.value.args[1] == [
        "string_field",
        "int_field",
        "child_model.string_field",
        "child_model.int_field",
    ]


def test_iter_model_formatted():
    model = ParentTestModel(
        string_field="test",
        int_field=0,
        child_model=ChildTestModel(string_field="child_test", int_field=1),
    )
    # default behavior should apply any json encoders on model
    assert list(iter_model_formatted(model, include=None, render=None)) == [
        ("string_field", "test"),
        ("int_field", "0.0"),
        (
            "child_model",
            ChildTestModel(string_field="child_test", int_field=1, grand_child=None),
        ),
    ]

    # default behavior when model is flattened
    assert list(iter_model_formatted(model, include=None, render=None, flat=True)) == [
        ("string_field", "test"),
        ("int_field", "0.0"),
        ("child_model.string_field", "child_test"),
        ("child_model.int_field", "1.0"),
        ("child_model.grand_child.string_field", None),
    ]

    # default behavior with 'include' filters
    assert list(
        iter_model_formatted(model, include=["string_field", "int_field"], render=None)
    ) == [
        ("string_field", "test"),
        ("int_field", "0.0"),
    ]

    # default behavior with 'include' filters _and_ flattened
    assert list(
        iter_model_formatted(
            model,
            include=["string_field", "child_model.int_field"],
            render=None,
            flat=True,
        )
    ) == [("string_field", "test"), ("child_model.int_field", "1.0")]

    # render string should apply matching callable defined in model Field
    assert list(iter_model_formatted(model, include=None, render="table")) == [
        ("string_field", "test"),
        ("int_field", "1"),
        (
            "child_model",
            ChildTestModel(string_field="child_test", int_field=1, grand_child=None),
        ),
    ]

    # render string should apply to child models when flattened
    assert list(
        iter_model_formatted(model, include=None, render="table", flat=True)
    ) == [
        ("string_field", "test"),
        ("int_field", "1"),
        ("child_model.string_field", "child_test"),
        ("child_model.int_field", "2"),
        ("child_model.grand_child.string_field", "None"),
    ]

    # render string with 'include' filters and flattened
    assert list(
        iter_model_formatted(
            model, include=["int_field", "child_model.*"], render="table", flat=True
        )
    ) == [
        ("int_field", "1"),
        ("child_model.string_field", "child_test"),
        ("child_model.int_field", "2"),
        ("child_model.grand_child.string_field", "None"),
    ]


def test_get_field_value_and_info():
    model = ParentTestModel(
        string_field="test",
        int_field=0,
        child_model=ChildTestModel(string_field="child_test", int_field=1),
    )
    value, field = get_field_value_and_info(model, ["int_field"])
    assert value == 0
    assert "table" in field.field_info.extra

    child_value, child_field = get_field_value_and_info(
        model, ["child_model", "int_field"]
    )
    assert child_value == 1
    assert "table" in child_field.field_info.extra

    empty_child_model = ParentTestModel(string_field="test", int_field=0)
    child_value, child_field = get_field_value_and_info(
        empty_child_model, ["child_model", "int_field"]
    )
    assert child_value is None
    assert "table" in child_field.field_info.extra

    grandchild_value, grandchild_field = get_field_value_and_info(
        empty_child_model, ["child_model", "grand_child", "string_field"]
    )
    assert grandchild_value is None
    assert "table" in grandchild_field.field_info.extra
