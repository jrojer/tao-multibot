from app.src.server.main import main
from app.src import env
import json

env.set_var("MASTER_CONFIG_PATH", "./master_config.json")
env.set_var("VAR_DIR", "./var")

with open(env.MASTER_CONFIG_PATH()) as f:
    infra = json.load(f)["infra"]

env.set_var("POSTGRES", infra["postgres"])
env.set_var("INFLUXDB", infra["influxdb"])

main()
