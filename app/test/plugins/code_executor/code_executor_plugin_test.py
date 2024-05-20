import pytest
import json
from app.src.plugins.code_executor.code_executor_plugin import CodeExecutorPlugin


@pytest.mark.asyncio
async def test_code_executor_plugin():
    plugin = CodeExecutorPlugin(timeout_seconds=120)
    code = """
for i in range(3):
    print(12345)
"""
    args = json.dumps({"code": code})
    result = await plugin.call("exec", args)
    result_dict = json.loads(result)

    assert result_dict["status"] == "completed"
    assert result_dict["returncode"] == 0
    assert result_dict["stdout"].strip() == "12345\n12345\n12345"
    assert result_dict["stderr"] == ""


@pytest.mark.asyncio
async def test_code_executor_plugin_timeout():
    plugin = CodeExecutorPlugin(timeout_seconds=10)
    code = """
import time
time.sleep(60)
print("This should not be printed")
"""
    args = json.dumps({"code": code})
    result = await plugin.call("exec", args)
    result_dict = json.loads(result)

    assert result_dict["status"] == "timeout"
    assert result_dict["returncode"] == -1
    assert result_dict["stdout"].strip() == ""
    assert "This should not be printed" not in result_dict["stderr"]


@pytest.mark.asyncio
async def test_code_executor_plugin_sigint_handling():
    plugin = CodeExecutorPlugin(timeout_seconds=10)
    code = """
import signal
import time

def handler(signum, frame):
    print("SIGINT captured")

signal.signal(signal.SIGINT, handler)
time.sleep(60)
print("This should not be printed")
"""
    args = json.dumps({"code": code})
    result = await plugin.call("exec", args)
    result_dict = json.loads(result)

    assert result_dict["status"] == "timeout"
    assert result_dict["returncode"] == -1
    assert "This should not be printed" not in result_dict["stderr"]
