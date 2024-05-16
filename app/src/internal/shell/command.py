import asyncio
import subprocess

from app.src.butter.checks import check_required
from app.src.observability.logger import Logger

logger = Logger(__name__)


class Command:
    def __init__(self, cmd: str | list[str]):
        if isinstance(cmd, list):
            self._cmd: list[str] = cmd
        else:
            self._cmd: list[str] = check_required(cmd, "cmd", str).split()
        self._stdout = ""
        self._stderr = ""
        self._returncode = 0

    def exec(self) -> "Command":
        logger.info("Executing command: %s", " ".join(self._cmd))
        result = subprocess.run(
            self._cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        self._stdout = result.stdout
        self._stderr = result.stderr
        self._returncode = result.returncode
        return self

    async def aexec(self) -> "Command":
        logger.info("Executing command: %s", " ".join(self._cmd))
        proc = await asyncio.create_subprocess_shell(
            " ".join(self._cmd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        self._stdout = stdout.decode()
        self._stderr = stderr.decode()
        self._returncode = check_required(proc.returncode, "returncode", int)
        return self

    def stdout(self) -> str:
        return self._stdout

    def stderr(self) -> str:
        return self._stderr

    def returncode(self) -> int:
        return self._returncode
