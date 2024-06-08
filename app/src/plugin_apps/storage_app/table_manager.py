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


# TODO: this class is responsible for the DATA_DIR
class TableManager:
    def __init__(self, chat_id: str, data_dir: Path = env.DATA_DIR()):
        self._chat_id: str = check_required(chat_id, "chat_id", str)
        db_path = data_dir / f"{chat_id}.db"
        self._sql_executor = SqlExecutor(db_path)
        self._data_dir = data_dir

    def execute_sql(self, sql: str) -> list[dict[str, str]]:
        result = self._sql_executor.execute(sql)
        tables = self.get_tables()
        for table_name in tables:
            if table_name in sql:
                self.sync_dataframe(table_name)
        return result.rowwise()
    
    def sync_dataframe(self, table_name: str) -> None:
        df_dir = self._data_dir / self._chat_id
        df_dir.mkdir(parents=True, exist_ok=True)
        data = self._sql_executor.execute(f"SELECT * FROM {table_name}").columnwise()
        pd.DataFrame(data).to_csv(df_dir / f"{table_name}.tsv", sep="\t", index=False)

    def sync_sqlite(self, table_name: str, df: pd.DataFrame) -> None:
        df.to_sql(table_name, self._sql_executor._conn, if_exists="replace", index=False) # type: ignore
        df_dir = self._data_dir / self._chat_id
        df_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(df_dir / f"{table_name}.tsv", sep="\t", index=False)
    
    def get_tables(self) -> dict[str, list[dict[str, Any]]]:
        d: dict[str, list[dict[str, Any]]] = {}
        tabels = self._sql_executor.execute("SELECT name FROM sqlite_master WHERE type='table';").rowwise()
        for table in tabels:
            res = self._sql_executor.execute(f"PRAGMA table_info({table["name"]})").rowwise()
            d[table["name"]] = res 
        return d

    @staticmethod
    def get_tsv_files_recursively(data_dir: Path = env.DATA_DIR()) -> list[dict[str, Any]]:
        files: list[dict[str, Any]] = []

        def recurse(dir: Path):
            for item in dir.iterdir():
                if item.is_dir():
                    recurse(item)
                else:
                    if item.suffix == ".tsv":
                        files.append(
                            {
                                "chat_id": dir.name, 
                                "table_name": item.stem, 
                                "df": pd.read_csv(item, sep="\t"), # type: ignore
                            }
                        )

        recurse(data_dir)
        return files
