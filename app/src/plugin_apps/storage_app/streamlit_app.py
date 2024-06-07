from pathlib import Path
from app.src import env
import pandas as pd
import streamlit as st
from app.src.observability.logger import Logger


logger = Logger(__name__)


def get_tsv_files_recursively_from(dir: Path) -> list[Path]:
    files: list[Path] = []

    def recurse(dir: Path):
        for item in dir.iterdir():
            if item.is_dir():
                recurse(item)
            else:
                if item.suffix == ".tsv":
                    files.append(item)

    recurse(dir)
    return files


def update(path_to_tsv: Path):
    logger.info("Data changed, args: %s", path_to_tsv)


def start_streamlit():
    tabs = []
    data_dir = env.DATA_DIR()
    files = get_tsv_files_recursively_from(data_dir)
    for file in files:
        df = pd.read_csv(file, sep="\t")
        tabs.append((file.stem, df, file))

    st_tabs = st.tabs([tab[0] for tab in tabs])
    i = 0
    for tab in st_tabs:
        with tab:
            st.header(tabs[i][0])
            df = tabs[i][1]
            st.data_editor(
                df, key=f"editor_{i}", num_rows="dynamic", on_change=update, args=(tabs[i][2],)
            )
        i += 1
