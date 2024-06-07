from pathlib import Path
import re
import sqlite3
from typing import Any

from app.src.butter.checks import check_required
from app.src.plugin_apps.storage_app.storage_plugin_server.sql_executor.operational_error import (
    OperationalError,
)


class SqlExecutor:
    def __init__(self, db_path: str | Path):
        check_required(db_path, "db_path", (str, Path))
        self._conn = sqlite3.connect(db_path)

    def execute(self, sql: str) -> list[dict[str, str]]:
        cursor = self._conn.cursor()
        try:
            cursor.execute(sql)
            self._conn.commit()
        except sqlite3.OperationalError as e:
            raise OperationalError(str(e))

        # re find SELECT statement as case-insensitive and replace it with SELECT:
        sql = re.sub(r"(?i)SELECT", "SELECT", sql)
        if "SELECT" in sql:
            columns = [item[0] for item in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            return []

    def get_tables(self) -> dict[str, list[dict[str, Any]]]:
        d = {}
        cursor = self._conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for table in cursor.fetchall():
            cursor.execute(f"PRAGMA table_info({table[0]})")
            d[table[0]] = cursor.fetchall()
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
