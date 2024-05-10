import pytest

from app.src.bot.repo.chat_messages_repository.chat_message import ChatMessage
from app.src.bot.repo.chat_messages_repository.postgres_chat_messages_repository import (
    PostgresChatMessagesRepository,
)
from app.test.bot.repo.chat_messages_repository.postgres_container import (
    setup_postgres_container,
    tear_down_postgres_container,
)


@pytest.fixture(scope="module", autouse=True)
def repo():
    setup_postgres_container()

    repo = PostgresChatMessagesRepository(
        host="localhost",
        port=5433,
        user="postgres",
        password="password",
        schemas="public",
    )

    repo.migrate()

    yield repo
    tear_down_postgres_container()


def test_should_add_and_fetch_messages(repo: PostgresChatMessagesRepository):
    # given
    message = a_message().content("AAARRR!").timestamp(1234567890).build()
    another_message = a_message().content("BBBRRR!").timestamp(1234567891).build()

    # when
    message_id = repo.add(message)
    another_message_id = repo.add(another_message)

    # then
    assert message_id is not None
    assert another_message_id is not None

    messages = repo.fetch_last_messages_by_chat_id(message.chat())
    assert len(messages) == 2
    assert messages[0] == message
    assert messages[1] == another_message


def a_message() -> ChatMessage.Builder:
    return (
        ChatMessage.new()
        .timestamp(1234567890)
        .content("Hello, world!")
        .content_type("text")
        .user("Some User")
        .chat("Some Chat")
        .source("telegram-bot")
        .role("user")
        .added_by("dev_bot")
    )
