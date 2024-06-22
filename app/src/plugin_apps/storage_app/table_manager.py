from pathlib import Path
from typing import Any
from app.src.butter.checks import check_required
from app.src.plugin_apps.storage_app.storage_plugin_server.sql_executor.sql_executor import (
    SqlExecutor,
)
from app.src import env
import pandas as pd
from app.src.observability.logger import Logger

logger = Logger(__name__)


# NOTE: this class is responsible for the DATA_DIR
class TableManager:
    def __init__(self, data_dir: Path = env.DATA_DIR()):
        self._data_dir = check_required(data_dir, "data_dir", Path)
        # TODO: this is a hot fix, consider proper implementation
        SqlExecutor(self._data_dir / "metadata.db").execute(f"CREATE TABLE IF NOT EXISTS chat_ids (chat_id TEXT PRIMARY KEY);")
        self._chat_ids = self._get_chat_ids()

    # TODO: consider returning constructed SqlExecutor object
    def execute_sql(self, sql: str, chat_id: str) -> list[dict[str, str]]:
        executor = SqlExecutor(self._get_db(chat_id))
        result = executor.execute(sql)
        return result.rowwise()

    def update_with_dataframe(self, table_name: str, chat_id: str, df: pd.DataFrame) -> None:
        executor = SqlExecutor(self._get_db(chat_id))
        df.to_sql(table_name, executor._conn, if_exists="replace", index=False) # type: ignore
    
    def get_tables(self, chat_id: str) -> dict[str, list[dict[str, Any]]]:
        executor = SqlExecutor(self._get_db(chat_id))
        d: dict[str, list[dict[str, Any]]] = {}
        tabels = executor.execute("SELECT name FROM sqlite_master WHERE type='table';").rowwise()
        for table in tabels:
            res = executor.execute(f"PRAGMA table_info({table["name"]})").rowwise()
            d[table["name"]] = res 
        return d

    def get_dataframes(self) -> list[dict[str, Any]]:
        files: list[dict[str, Any]] = []
        chat_ids = self._get_chat_ids()
        for chat_id in chat_ids:
            executor = SqlExecutor(self._get_db(chat_id))
            tables = executor.execute("SELECT name FROM sqlite_master WHERE type='table';").rowwise()
            for table in tables:
                table_name = table["name"]
                df = pd.DataFrame(executor.execute(f"SELECT * FROM {table_name};").columnwise())
                files.append({"chat_id": chat_id, "table_name": table_name, "df": df})
        return files

    def _get_db(self, chat_id: str) -> Path:
        if chat_id not in self._chat_ids:
            self._chat_ids.add(chat_id)
            self._update_chat_ids(chat_id)
        return self._data_dir / f"{chat_id}.db"
    
    def _update_chat_ids(self, chat_id: str) -> None:
        executor = SqlExecutor(self._data_dir / "metadata.db")
        executor.execute(f"CREATE TABLE IF NOT EXISTS chat_ids (chat_id TEXT PRIMARY KEY);")
        executor.execute(f"INSERT OR IGNORE INTO chat_ids (chat_id) VALUES ('{chat_id}');")

    def _get_chat_ids(self) -> set[str]:
        executor = SqlExecutor(self._data_dir / "metadata.db")
        return set(d["chat_id"] for d in executor.execute("SELECT chat_id FROM chat_ids;").rowwise())
