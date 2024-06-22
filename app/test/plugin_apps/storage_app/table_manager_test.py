from pathlib import Path
import pytest
from app.src import env
from app.src.plugin_apps.storage_app.table_manager import TableManager


@pytest.fixture
def fixture():
    chat_id = "test_table_manager"
    data_dir = env.DATA_DIR() / "test"
    data_dir.mkdir(parents=True, exist_ok=True)
    tmp_db = data_dir / f"{chat_id}.db"
    df_dir = data_dir / chat_id
    df_tsv = df_dir / "test.tsv"
    tmp_db.touch()
    tmp_db.unlink()
    yield chat_id, data_dir
    tmp_db.unlink()
    df_tsv.unlink()
    df_dir.rmdir()
    data_dir.rmdir()


def test_table_manager(fixture: tuple[str, Path]):
    chat_id = fixture[0]
    data_dir = fixture[1]
    tm = TableManager(data_dir)

    tm.execute_sql("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);", chat_id)
    tm.execute_sql("INSERT INTO test (name) VALUES ('test');", chat_id)
    tm.execute_sql("INSERT INTO test (name) VALUES ('test2');", chat_id)

    items = tm.execute_sql("SELECT * FROM test;", chat_id)

    assert len(items) == 2
    assert items[0]["id"] == 1
    assert items[0]["name"] == "test"
    assert items[1]["id"] == 2
    assert items[1]["name"] == "test2"

    assert tm.get_tables(chat_id) == {
        "test": [
            {
                "cid": 0,
                "name": "id",
                "type": "INTEGER",
                "notnull": False,
                "dflt_value": None,
                "pk": True,
            },
            {
                "cid": 1,
                "name": "name",
                "type": "TEXT",
                "notnull": False,
                "dflt_value": None,
                "pk": False,
            },
        ]
    }


def test_update_with_dataframe(fixture: tuple[str, Path]):
    chat_id = fixture[0]
    data_dir = fixture[1]
    tm = TableManager(data_dir)

    tm.execute_sql("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);", chat_id)
    tm.execute_sql("INSERT INTO test (name) VALUES ('test');", chat_id)
    tm.execute_sql("INSERT INTO test (name) VALUES ('test2');", chat_id)

    files = tm.get_dataframes()

    assert len(files) == 1
    for file in files:
        assert file["df"].shape[0] == 2

    df = files[0]["df"]
    df.at[0, "name"] = "updated_test"
    tm.update_with_dataframe("test", chat_id, df)

    result = tm.execute_sql("SELECT * FROM test;", chat_id)
    assert len(result) == 2
    assert result[0]["name"] == "updated_test"
    assert result[1]["name"] == "test2"



def test_sql_get_tables_on_empty_db(fixture: tuple[str, Path]):
    chat_id = fixture[0]
    data_dir = fixture[1]
    tm = TableManager(data_dir)
    assert tm.get_tables(chat_id) == {}

def test_get_dataframes_on_empty_table(fixture: tuple[str, Path]):
    chat_id = fixture[0]
    data_dir = fixture[1]
    tm = TableManager(data_dir)
    tm.execute_sql("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);", chat_id)
    dfs = tm.get_dataframes()
    assert len(dfs) == 1
    assert chat_id == dfs[0]["chat_id"]
    assert "test" == dfs[0]["table_name"]
    assert dfs[0]["df"].empty
