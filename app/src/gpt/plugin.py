from abc import ABC, abstractmethod
from typing import List, Dict

from app.src.butter.checks import check_json, check_required


class Plugin(ABC):
    class CallParams:
        class Builder:
            def __init__(self):
                self._function_name = None
                self._arguments_json = None

            def function_name(self, function_name):
                self._function_name = function_name
                return self

            def arguments_json(self, arguments_json):
                self._arguments_json = arguments_json
                return self

            def build(self):
                return Plugin.CallParams(self)
            
        @staticmethod
        def new() -> "Plugin.CallParams.Builder":
            return Plugin.CallParams.Builder()

        def __init__(self, builder: Builder):
            self._function_name = check_required(
                builder._function_name, "function_name", str
            )
            self._arguments_json = check_required(builder._arguments_json, "arguments_json", str)
            check_json(self._arguments_json, "arguments_json")

        def function_name(self) -> str:
            return self._function_name

        def arguments_json(self) -> str:
            return self._arguments_json

    @abstractmethod
    def functions(self) -> List[Dict]:
        pass

    @abstractmethod
    def call(self, params: CallParams) -> str:
        pass
