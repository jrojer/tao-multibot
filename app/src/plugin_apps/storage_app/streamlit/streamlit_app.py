from typing import Optional
import streamlit as st
from app.src.observability.logger import Logger
from app.src.plugin_apps.storage_app.streamlit.auth import check_password, logout
from app.src.plugin_apps.storage_app.streamlit.utils import hide_menu
from app.src.plugin_apps.storage_app.table_manager import TableManager

logger = Logger(__name__)

_TM = TableManager()

# TODO: add chat names for better UX


def update(chat_id: str, table_name: str) -> None:
    def _get_row_id(row_number: int) -> Optional[str]:
        rowids = _TM.execute_sql(f"SELECT rowid FROM {table_name} LIMIT 1 OFFSET {row_number}", chat_id)
        if len(rowids) == 0:
            logger.warning(f"rowid not found for row_number: {row_number}")
            return None
        return rowids[0]["rowid"]

    key = f"{table_name}_{chat_id}"
    changes = st.session_state[key]
    for row_number, columns in changes["edited_rows"].items():
        for column_name, value in columns.items():
            row_id = _get_row_id(row_number)
            if row_id is None:
                continue
            sql = f"UPDATE {table_name} SET {column_name} = '{value}' WHERE rowid = {row_id}"
            _TM.execute_sql(sql, chat_id)

    for columns in changes["added_rows"]:
        for column_name, value in columns.items():
            sql = f"INSERT INTO {table_name} ({column_name}) VALUES ('{value}')"
            _TM.execute_sql(sql, chat_id)
    for row_number in changes["deleted_rows"]:
        row_id = _get_row_id(row_number)
        sql = f"DELETE FROM {table_name} WHERE rowid = {row_id}"
        _TM.execute_sql(sql, chat_id)
    

def start_streamlit():
    st.set_page_config("/A", "⭕")
    hide_menu()

    if not check_password():
        st.stop()
        
    files = _TM.get_dataframes()
    if len(files) == 0:
        st.write("No tables found") # type: ignore
        return
    # TODO: consider refactor st.tabs usage
    st_tabs = st.tabs([file["table_name"] for file in files])
    for tab, file in zip(st_tabs, files):
        with tab:
            st.header(file["table_name"])
            st.data_editor(
                file["df"],
                key=f"{file["table_name"]}_{file["chat_id"]}",
                num_rows="dynamic",
                on_change=update,
                args=(file["chat_id"], file["table_name"]),
            )
    
    st.button("Logout", on_click=logout)
