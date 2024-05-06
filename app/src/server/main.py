from app.src.server.master_config.master_config import MasterConfig
from app.src.server.runtime_manager import RuntimeManager


def main():
    master_config = MasterConfig()
    runtime_manager = RuntimeManager(master_config)
    runtime_manager.start_all()
