import streamlit as st
from uuid import uuid4
from streamlit_cookies_controller import CookieController  # type: ignore
import hashlib
from app.src import env

controller = CookieController()


def hash_password(password: str):
    password_bytes = password.encode("utf-8")
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()


@st.cache_data(ttl=env.STREAMLIT_TTL_SECONDS())
def _token() -> str:
    return str(uuid4())


def check_password():
    tkn = controller.get("customAuthToken")
    if tkn == _token():
        return True

    def password_entered():
        st.session_state["password_correct"] = False
        if hash_password(st.session_state["password"]) == env.STREAMLIT_TOKEN():
            st.session_state["password_correct"] = True
            del st.session_state["password"]

    if st.session_state.get("password_correct", False):
        tkn = _token()
        controller.set("customAuthToken", tkn)
        return True

    st.text_input(
        "Password",
        type="password",
        on_change=password_entered,
        key="password",
        label_visibility="collapsed",
    )
    return False


def logout() -> None:
    st.session_state["password_correct"] = False
    controller.remove("customAuthToken")
