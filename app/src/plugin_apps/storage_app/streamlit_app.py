from app.src import env
import pandas as pd
import streamlit as st
from app.src.observability.logger import Logger


logger = Logger(__name__)


def start_streamlit():
    df = pd.read_csv(env.DATA_DIR() / "data.csv")  # type: ignore
    st.title("My Streamlit App")
    st.write(df)  # type: ignore
