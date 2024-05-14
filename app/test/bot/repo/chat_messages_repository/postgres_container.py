from time import sleep

from app.src.internal.shell.command import Command


CONTAINER_NAME = "tao_test_postgres"
PORT = 5433


def _remove_container():
    Command(f"docker stop {CONTAINER_NAME}").exec()
    Command(f"docker rm {CONTAINER_NAME}").exec()


def _create_database(db_name: str):
    Command(f"docker exec {CONTAINER_NAME} createdb -U postgres {db_name}").exec()


def setup_postgres_container():
    _remove_container()
    # Start a Postgres container
    Command(
        f"docker run --name {CONTAINER_NAME} -e POSTGRES_PASSWORD=password -p {PORT}:5432 -d postgres"
    ).exec()

    # Wait for the container to be ready
    sleep(10.0)  # 10 seconds

    _create_database("platform")


def tear_down_postgres_container():
    _remove_container()
