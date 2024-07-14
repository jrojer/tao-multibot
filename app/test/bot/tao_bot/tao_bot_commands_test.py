from app.src.bot.tao_bot.content_type import ContentType
from app.src.bot.tao_bot.tao_bot_commands import TaoBotCommands
from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.test.fixtures.mock_conf_client import MockConfClient
from app.test.fixtures.mock_gpt_conf import MockGptConf
from app.test.fixtures.mock_tao_bot_conf import MockTaoBotConf


def test_is_command_for():
    conf_client = MockConfClient()
    tao_bot_conf = MockTaoBotConf()
    gpt_conf = MockGptConf()
    cmds = TaoBotCommands(conf_client, tao_bot_conf, gpt_conf)
    tao_bot_update = (
        TaoBotUpdate.new()
        .chat_id("chat1")
        .chat_name("chat1_name")
        .from_user("user1")
        .content("/start@bot_name")
        .content_type(ContentType.TEXT)
        .timestamp(123456789)
        .build()
    )
    assert cmds._is_command_for("bot_name", tao_bot_update) == True  # type: ignore
