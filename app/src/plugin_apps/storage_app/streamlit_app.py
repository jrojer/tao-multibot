from pathlib import Path
from typing import Any
from app.src import env
import pandas as pd
import streamlit as st
from app.src.observability.logger import Logger
from app.src.plugin_apps.storage_app.table_manager import TableManager


logger = Logger(__name__)


def get_tsv_files_recursively_from(dir: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []

    def recurse(dir: Path):
        for item in dir.iterdir():
            if item.is_dir():
                recurse(item)
            else:
                if item.suffix == ".tsv":
                    files.append(
                        {"chat_id": dir.name, "table_name": item.stem, "path": item}
                    )

    recurse(dir)
    return files


def _update(chat_id: str, table_name: str):
    TableManager(chat_id).sync_sqlite(table_name)


def start_streamlit():
    data_dir = env.DATA_DIR()
    files = get_tsv_files_recursively_from(data_dir)

    # TODO: consider refactor st.tabs usage
    st_tabs = st.tabs([file["table_name"] for file in files])
    for tab, file in zip(st_tabs, files):
        with tab:
            st.header(file["table_name"])
            df = pd.read_csv(file["path"], sep="\t") # type: ignore
            st.data_editor(
                df,
                key=file["table_name"],
                num_rows="dynamic",
                on_change=_update,
                args=(file["chat_id"], file["table_name"]),
            )
