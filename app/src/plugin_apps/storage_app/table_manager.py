from typing import Any
from app.src.butter.checks import check_required
from app.src.plugin_apps.storage_app.storage_plugin_server.sql_executor.sql_executor import (
    SqlExecutor,
)
from app.src import env
import pandas as pd


class TableManager:
    def __init__(self, chat_id: str):
        self._chat_id = check_required(chat_id, "chat_id", str)
        db_path = env.DATA_DIR() / f"{chat_id}.db"
        self._sql_executor = SqlExecutor(db_path)

    def execute_sql(self, sql: str) -> list[dict[str, str]]:
        result = self._sql_executor.execute(sql)
        tables = self._sql_executor.get_tables()
        for table_name in tables:
            if table_name in sql:
                self.sync_dataframe(table_name)
        return result
    
    def sync_dataframe(self, table_name: str) -> None:
        df_dir = env.DATA_DIR() / self._chat_id
        df_dir.mkdir(parents=True, exist_ok=True)
        data = self._sql_executor.execute(f"SELECT * FROM {table_name}")
        pd.DataFrame(data).to_csv(df_dir / f"{table_name}.tsv", sep="\t", index=False)

    def sync_sqlite(self, table_name: str) -> None:
        df_dir = env.DATA_DIR() / self._chat_id
        data = pd.read_csv(df_dir / f"{table_name}.tsv", sep="\t") # type: ignore
        data.to_sql(table_name, self._sql_executor._conn, if_exists="replace", index=False) # type: ignore
    
    # TODO: to be moved from SqlExecutor
    def _get_tables(self) -> dict[str, list[dict[str, Any]]]:
        d = {}
        res = self._sql_executor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for _ in res:
            # self._sql_executor.execute(f"PRAGMA table_info({table[0]})")
            # d[table[0]] = cursor.fetchall()  
            pass
        return {
            table: [
                {
                    "name": name,
                    "type": type_,
                    "notnull": bool(notnull), # type: ignore
                    "default": default,
                    "pk": bool(pk), # type: ignore
                }
                for cid, name, type_, notnull, default, pk in d[table] # type: ignore
            ]
            for table in d # type: ignore
        }
