import pytest
from notion_sugar.core.decorators import Page, Database
from notion_sugar.core.errors import ValidationError
from notion_sugar.core.fields import Field


def test_page_decorator_validates_required_fields():
    @Page
    class TestPage:
        title = Field(type="title", required=True)
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    with pytest.raises(ValidationError) as exc:
        TestPage()
    assert "Required field title is not set" in str(exc.value)


def test_page_decorator_validates_select_field_options():
    @Page
    class TestPage:
        status = Field(type="select", options=["Done", "In Progress"])
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    with pytest.raises(ValidationError):
        TestPage(status="Invalid")


def test_page_decorator_accepts_valid_select_value():
    @Page
    class TestPage:
        status = Field(type="select", options=["Done", "In Progress"])
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    page = TestPage(status="Done")
    assert page.status == "Done"


def test_database_decorator_preserves_existing_values():
    @Database
    class TestDatabase:
        title: str
        description: str
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    db = TestDatabase(title="Test")
    assert db.title == "Test"
    assert db.description is None


def test_database_decorator_initializes_missing_fields():
    @Database
    class TestDatabase:
        title: str
        description: str

    db = TestDatabase()
    assert hasattr(db, "title")
    assert hasattr(db, "description")
    assert db.title is None
    assert db.description is None


def test_database_decorator_preserves_existing_values():
    @Database
    class TestDatabase:
        title: str
        description: str

    db = TestDatabase(title="Test")
    assert db.title == "Test"
    assert db.description is None