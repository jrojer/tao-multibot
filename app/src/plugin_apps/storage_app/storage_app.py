import sys
# NOTE: this helps streamlit process to locate the required modules
sys.path.append(__file__.split("app/src")[0])

import signal
from app.src.butter.checks import check_required
import subprocess

from app.src.observability.logger import Logger
from app.src.plugin_apps.storage_app.storage_plugin_server.storage_plugin_server import (
    StoragePluginServer,
)
from app.src.plugin_apps.storage_app.streamlit_app import start_streamlit


logger = Logger(__name__)


_PLUGIN_SEVER_PORT = 8889
_STREAMLIT_PORT = 8501


class StorageApp:
    def __init__(self):
        self._streamlit_process: subprocess.Popen[bytes]
        self._storage_plugin_server = StoragePluginServer(_PLUGIN_SEVER_PORT)

    def start(self):
        self._streamlit_process = subprocess.Popen(
            [
                "streamlit",
                "run",
                __file__,
                "--server.headless",
                "true",
                f"--server.port={_STREAMLIT_PORT}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._storage_plugin_server.start()

    def stop(self):
        check_required(self._streamlit_process, "Running streamlit process")
        self._streamlit_process.send_signal(signal.SIGINT)
        self._storage_plugin_server.stop()

    def join(self):
        self._streamlit_process.communicate()
        self._storage_plugin_server.join()


if __name__ == "__main__":
    start_streamlit()
