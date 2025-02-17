import pytest
from unittest.mock import Mock, patch
from notion_client import Client
from notion_sugar.core.client import NotionSugar
from notion_sugar.core.errors import NotionSugarError


@pytest.fixture
def valid_token():
    return "secret_test_valid_token_123"


def test_notion_sugar_initializes_with_valid_token(valid_token):
    sugar = NotionSugar(valid_token)
    assert isinstance(sugar.client, Client)
    assert sugar.auth_token == valid_token


def test_notion_sugar_raises_error_on_invalid_token():
    with pytest.raises(NotionSugarError):
        NotionSugar("")


def test_notion_sugar_raises_error_when_client_init_fails():
    with patch("notion_client.Client", side_effect=Exception("Client error")):
        with pytest.raises(NotionSugarError) as exc:
            NotionSugar("valid_token")
        assert "Failed to initialize client" in str(exc.value)


def test_db_returns_database_query_with_valid_id(valid_token):
    sugar = NotionSugar(valid_token)
    database_id = "8a8e5a45-c974-4cab-938b-31e6c8025bcb"
    query = sugar.db(database_id)
    assert query.database_id == database_id
    assert query.client == sugar.client


def test_db_raises_error_with_invalid_database_id(valid_token):
    sugar = NotionSugar(valid_token)
    with pytest.raises(NotionSugarError):
        sugar.db("invalid-id")