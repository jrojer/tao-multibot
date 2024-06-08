import streamlit as st
from app.src.observability.logger import Logger
from app.src.plugin_apps.storage_app.table_manager import TableManager

logger = Logger(__name__)


def start_streamlit():
    files = TableManager.get_tsv_files_recursively()

    # TODO: consider refactor st.tabs usage
    st_tabs = st.tabs([file["table_name"] for file in files])
    for tab, file in zip(st_tabs, files):
        with tab:
            st.header(file["table_name"])
            df = file["df"]
            updated = st.data_editor(
                df,
                key=file["table_name"],
                num_rows="dynamic",
            )
        if not updated.equals(df):
            TableManager(file["chat_id"]).sync_sqlite(file["table_name"], updated)
