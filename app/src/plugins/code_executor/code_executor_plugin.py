import asyncio
import json
from pathlib import Path
from typing import Any, Callable, Coroutine, Optional
from app.src.butter.checks import check_optional, check_required, check_that
from app.src.gpt.plugin import Plugin
from app.src import env
import subprocess
import time
import random
import string

from app.src.observability.logger import Logger


logger = Logger(__name__)

ASYNC_CALLBACK = Callable[[str], Coroutine[str, None, None]]


class CodeExecutorPlugin(Plugin):
    def __init__(
        self, timeout_seconds: int = 120, on_success: Optional[ASYNC_CALLBACK] = None
    ):
        self._timeout_seconds: int = check_required(
            timeout_seconds, "timeout_seconds", int
        )
        self._on_success: Optional[ASYNC_CALLBACK] = on_success

    @staticmethod
    def name() -> str:
        return "code_executor"

    def functions(self) -> list[dict[str, Any]]:
        return [
            {
                "manifest": {
                    "name": "exec",
                    "description": "Executes python code.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Python code to execute.",
                            },
                        },
                        "required": ["code"],
                    },
                }
            }
        ]

    def is_delegate(self) -> bool:
        return False
    
    async def system_prompt_attachment(self) -> Optional[str]:
        return None

    async def call(self, name: str, args: str) -> str:
        logger.info("Calling function %s with args %s", name, args)
        check_that(name == "exec", f"Unknown function {name}")
        try:
            d: dict[str, str] = json.loads(args)
            check_optional(d, "d", dict)
            code = check_required(d.get("code"), "code", str)
        except Exception as e:
            logger.warning("Failed to parse args: %s", args, exc_info=e)
            return json.dumps(
                {
                    "message": 'format: {"code": "<python code>"}',
                    "status": "failed",
                    "error": str(e),
                }
            )

        # NOTE: https://stackoverflow.com/questions/33908794/get-value-of-last-expression-in-exec-call
        script = f"""
import ast
def exec_with_return(code: str, globals, locals):
    a = ast.parse(code)
    last_expression = None
    if a.body:
        if isinstance(a_last := a.body[-1], ast.Expr):
            last_expression = ast.unparse(a.body.pop())
        elif isinstance(a_last, ast.Assign):
            last_expression = ast.unparse(a_last.targets[0])
        elif isinstance(a_last, (ast.AnnAssign, ast.AugAssign)):
            last_expression = ast.unparse(a_last.target)
    exec(ast.unparse(a), globals, locals)
    if last_expression:
        return eval(last_expression, globals, locals)

val = exec_with_return({code!r}, globals(), locals())
if val is not None:
    print(val)
"""
        logger.info("Executing code: %s", code)

        random_id: str = _random_alphanumeric(8)
        container_name: str = f"code_executor_{random_id}"
        tmp_dir: Path = env.TMP_DIR() / "code_executor" / random_id
        tmp_dir.mkdir(parents=True, exist_ok=True)

        with open(tmp_dir / "script.py", "w") as f:
            f.write(script)

        image_name = "code_executor"

        build_command = [
            "docker",
            "build",
            "-t",
            image_name,
            str(Path(__file__).parent),
        ]
        p = subprocess.run(
            build_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if p.returncode != 0:
            logger.error("Failed to build docker image: %s", p.stderr.decode())
            return json.dumps(
                {
                    "status": "failed",
                    "error": "Failed to build docker image",
                }
            )

        command = [
            "docker",
            "run",
            "--rm",
            "--name",
            container_name,
            "-v",
            f"{tmp_dir.absolute()}:/usr/src/app",
            image_name,
            "python",
            "/usr/src/app/script.py",
        ]

        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        start_time = time.time()

        result: dict[str, Any] = {}
        while True:
            returncode = process.poll()
            if returncode is not None:
                stdout, stderr = process.communicate()
                result = {
                    "status": "completed",
                    "returncode": returncode,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
                if self._on_success is not None:
                    await self._on_success(result["stdout"])
                if len(result["stdout"]) == 0:
                    logger.warning("No output from code execution")
                logger.info("stdout: %s", result["stdout"])
                logger.info("stderr: %s", result["stderr"])
                break
            elif time.time() - start_time > self._timeout_seconds:
                subprocess.run(
                    [
                        "docker",
                        "stop",
                        container_name,
                    ]
                )

                subprocess.run(
                    [
                        "docker",
                        "rm",
                        container_name,
                    ]
                )

                stdout, stderr = process.communicate()
                result = {
                    "status": "timeout",
                    "returncode": -1,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                }
                logger.warning("Code execution timed out")
                break
            else:
                await asyncio.sleep(1)

        _remove_directory(tmp_dir)
        return json.dumps(result)


def _random_alphanumeric(length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _remove_directory(directory_path: Path) -> None:
    for item in directory_path.iterdir():
        if item.is_dir():
            _remove_directory(item)
        else:
            item.unlink()
    directory_path.rmdir()
