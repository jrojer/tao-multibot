from app.src.plugin_apps.storage_app.storage_plugin_server.resources.execute_sql_resource import (
    ExecuteSqlResource,
)
import pytest
from app.src import env
from app.src.plugin_apps.storage_app.storage_plugin_server.sql_executor.sql_executor import (
    SqlExecutor,
)


class MockRequest:
    class MockMatchInfo:
        def __init__(self, chat_id: str):
            self.chat_id = chat_id

        def get(self, key) -> str:  # type: ignore
            return self.chat_id

    def __init__(self, chat_id: str):
        self.match_info = MockRequest.MockMatchInfo(chat_id)

    async def json(self):
        return {"sql": "SELECT * FROM test;"}


@pytest.fixture
def chat_id():
    chat_id = "test_sql_executor"
    tmp_db = env.DATA_DIR() / f"{chat_id}.db"
    df_dir = env.DATA_DIR() / chat_id
    test_tsv = df_dir / "test.tsv"
    tmp_db.touch()
    tmp_db.unlink()
    executor = SqlExecutor(tmp_db)
    executor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);")
    executor.execute(
        "CREATE TABLE another_table (id INTEGER PRIMARY KEY, field TEXT, date DATETIME);"
    )
    executor.execute("INSERT INTO test (name) VALUES ('test');")
    executor.execute("INSERT INTO test (name) VALUES ('test2');")
    executor.execute(
        "INSERT INTO another_table (field, date) VALUES ('test', '2021-01-01');"
    )
    yield chat_id
    tmp_db.unlink()
    test_tsv.unlink()
    df_dir.rmdir()


async def test_execute_sql_resource(chat_id: str):
    resource = ExecuteSqlResource()

    handler = resource.handler()

    req = MockRequest(chat_id)

    res = await handler(req)  # type: ignore

    assert res.status == 200
