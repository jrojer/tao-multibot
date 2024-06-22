import pytest
from app.src.plugin_apps.storage_app.storage_plugin_server.sql_executor.sql_executor import (
    SqlExecutor,
)
from pathlib import Path


@pytest.fixture
def tmp_db():
    tmp_db = Path("test_sql_executor.db")
    tmp_db.touch()
    tmp_db.unlink()
    yield tmp_db
    tmp_db.unlink()


def test_sql_executor(tmp_db: Path):
    executor = SqlExecutor(tmp_db)

    executor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);")
    executor.execute("INSERT INTO test (name) VALUES ('test');")
    executor.execute("INSERT INTO test (name) VALUES ('test2');")

    items = executor.execute("SELECT * FROM test;").rowwise()

    assert len(items) == 2
    assert items[0]["id"] == 1
    assert items[0]["name"] == "test"
    assert items[1]["id"] == 2
    assert items[1]["name"] == "test2"
