from app.src.env import init_env


init_env("./master.json", "./var")
from app.src.server.main import main

main()
