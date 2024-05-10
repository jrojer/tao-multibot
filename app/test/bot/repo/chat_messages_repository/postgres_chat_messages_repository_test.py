import pytest

from app.src.bot.repo.chat_messages_repository.postgres_chat_messages_repository import (
    PostgresChatMessagesRepository,
)
from app.test.bot.repo.chat_messages_repository.postgres_container import (
    setup_postgres_container,
    tear_down_postgres_container,
)


@pytest.fixture(scope="module", autouse=True)
def setup_environment():
    setup_postgres_container()
    yield
    tear_down_postgres_container()


def test_should_migrate_chat_messages_db():
    repo = PostgresChatMessagesRepository(
        host="localhost",
        port=5433,
        user="postgres",
        password="password",
        schemas="public",
    )

    repo.migrate()
