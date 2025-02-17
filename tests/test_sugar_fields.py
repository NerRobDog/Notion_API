import pytest
from notion_sugar.core.fields import Field, FieldFactory, field


def test_field_creates_title_field_with_correct_type():
    title_field = field.title()
    assert title_field.type == "title"
    assert title_field.required is False
    assert title_field.options is None
    assert title_field.default is None


def test_field_creates_text_field_with_correct_type():
    text_field = field.text()
    assert text_field.type == "rich_text"
    assert text_field.required is False
    assert text_field.options is None


def test_select_field_stores_options():
    options = ["Option1", "Option2"]
    select_field = field.select(options)
    assert select_field.type == "select"
    assert select_field.options == options


def test_field_creates_date_field_with_correct_type():
    date_field = field.date()
    assert date_field.type == "date"
    assert date_field.required is False


def test_field_creates_person_field_with_correct_type():
    person_field = field.person()
    assert person_field.type == "people"
    assert person_field.required is False


def test_field_with_default_value_stores_default():
    field = Field(type="title", default="Default Title")
    assert field.default == "Default Title"


def test_required_field_stores_required_flag():
    field = Field(type="rich_text", required=True)
    assert field.required is True


def test_field_with_empty_options_list_stores_empty_list():
    field = Field(type="select", options=[])
    assert field.options == []