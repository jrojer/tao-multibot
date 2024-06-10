from pathlib import Path
import sqlite3
from typing import Any

from app.src.butter.checks import check_required
from app.src.plugin_apps.storage_app.storage_plugin_server.sql_executor.operational_error import (
    OperationalError,
)

_connection_cache: dict[str, sqlite3.Connection] = {}


class SqlExecutor:
    class Output:
        def __init__(self):
            self.columns: list[str] = []
            self.rows: list[list[Any]] = []

        def rowwise(self) -> list[dict[str, Any]]:
            return [dict(zip(self.columns, row)) for row in self.rows]

        def columnwise(self) -> dict[str, list[Any]]:
            return {column: [row[i] for row in self.rows] for i, column in enumerate(self.columns)}
        
        def empty(self) -> bool:
            return len(self.columns) == 0
        
    @staticmethod
    def output(columns: list[str], rows: list[list[Any]]) -> Output:
        obj = SqlExecutor.Output()
        obj.columns = columns
        obj.rows = rows
        return obj
    
    @staticmethod
    def empty_output() -> Output:
        return SqlExecutor.Output()

    def __init__(self, db_path: str | Path):
        check_required(db_path, "db_path", (str, Path))
        if db_path not in _connection_cache:
            _connection_cache[str(db_path)] = sqlite3.connect(db_path)
        self._conn = _connection_cache[str(db_path)]

    def execute(
        self, sql: str
    ) -> Output:
        cursor = self._conn.cursor()
        try:
            cursor.execute(sql)
            self._conn.commit()
        except sqlite3.OperationalError as e:
            raise OperationalError(str(e))

        if cursor.description is not None:
            columns = [item[0] for item in cursor.description]
            rows = cursor.fetchall()
            return self.output(columns, rows)
        else:
            return self.empty_output()
