from typing import Any, Optional
from app.src.butter.checks import (
    check_any_present,
    check_one_of,
    check_required,
    check_type,
)
import unicodedata

from app.src.gpt.tokeniser import Tokeniser


ARGUMENTS = "arguments"
ASSISTANT = "assistant"
CHOICES = "choices"
COMPLETION_TOKENS = "completion_tokens"
CONTENT = "content"
FUNCTION = "function"
FUNCTION_CALL = "function_call"
FUNCTION_NAME = "name"
MESSAGE = "message"
NAME = "name"
PROMPT_TOKENS = "prompt_tokens"
ROLE = "role"
SYSTEM = "system"
USAGE = "usage"
USER = "user"


def _is_latin(char: str):
    return unicodedata.name(char).startswith(("LATIN", "COMMON"))


def _safe_format_username(username: Optional[str]):
    if username is None:
        return None
    # make username match ^[a-zA-Z0-9_-]{1,64}$
    name = "".join(
        filter(
            lambda c: _is_latin(c) or c.isdecimal() or c == "_" or c == "-", username
        )
    )
    if len(name) == 0:
        return "user_with_unreadable_name"
    # ensure the length is less than 64
    return name[:64]


class ChatformMessage:
    class Usage:
        class Builder:
            def __init__(self) -> None:
                self._completion_tokens: Optional[int] = None
                self._prompt_tokens: Optional[int] = None

            def completion_tokens(self, value: int) -> "ChatformMessage.Usage.Builder":
                self._completion_tokens = value
                return self

            def prompt_tokens(self, value: int) -> "ChatformMessage.Usage.Builder":
                self._prompt_tokens = value
                return self

            def build(self) -> "ChatformMessage.Usage":
                return ChatformMessage.Usage(self)

        def __init__(self, builder: Builder):
            self._completion_tokens = check_required(
                builder._completion_tokens, COMPLETION_TOKENS, int # type: ignore
            )
            self._prompt_tokens = check_required(
                builder._prompt_tokens, PROMPT_TOKENS, int # type: ignore
            )

        def completion_tokens(self) -> int:
            return self._completion_tokens

        def prompt_tokens(self) -> int:
            return self._prompt_tokens

    class FunctionCall:
        class Builder:
            def __init__(self):
                self._name = None
                self._arguments = None

            def name(self, name: str) -> "ChatformMessage.FunctionCall.Builder":
                self._name = name
                return self

            def arguments(
                self, arguments: str
            ) -> "ChatformMessage.FunctionCall.Builder":
                self._arguments = arguments
                return self

            def build(self) -> "ChatformMessage.FunctionCall":
                return ChatformMessage.FunctionCall(self)

        def __init__(self, builder: Builder):
            self._name = check_required(builder._name, FUNCTION_NAME, str) # type: ignore
            self._arguments = check_required(builder._arguments, ARGUMENTS, str) # type: ignore

        def name(self) -> str:
            return self._name

        def arguments(self) -> str:
            return self._arguments

        def to_dict(self) -> dict[str, Any]:
            return {
                FUNCTION_NAME: self._name,
                ARGUMENTS: self._arguments,
            }

    class Builder:
        def __init__(self):
            self._role: Optional[str] = None
            self._content: Optional[str] = None
            self._name: Optional[str] = None
            self._function_call: Optional["ChatformMessage.FunctionCall"] = None
            self._usage: Optional["ChatformMessage.Usage"] = None

        def role(self, role: str) -> "ChatformMessage.Builder":
            self._role = role
            return self

        def content(self, content: str) -> "ChatformMessage.Builder":
            self._content = content
            return self

        def name(self, name: Optional[str]) -> "ChatformMessage.Builder":
            self._name = name
            return self

        def function_call(self, function_call: "ChatformMessage.FunctionCall") -> "ChatformMessage.Builder":
            self._function_call = function_call
            return self

        def usage(self, usage: "ChatformMessage.Usage") -> "ChatformMessage.Builder":
            self._usage = usage
            return self

        def build(self):
            return ChatformMessage(self)

    def __init__(self, builder: Builder):
        self._role = check_one_of(
            check_required(builder._role, ROLE, str), # type: ignore
            ROLE,
            [SYSTEM, USER, ASSISTANT, FUNCTION],
        )
        self._content = check_required(builder._content, CONTENT, str) # type: ignore
        self._name = _safe_format_username(check_type(builder._name, NAME, str)) # type: ignore
        self._function_call = check_type(
            builder._function_call, FUNCTION_CALL, ChatformMessage.FunctionCall # type: ignore
        )
        check_any_present(
            [self._content, self._function_call], [CONTENT, FUNCTION_CALL]
        )
        self._usage = check_type(builder._usage, USAGE, ChatformMessage.Usage) # type: ignore

    def role(self) -> str:
        return self._role

    def content(self) -> str:
        return self._content

    def name(self) -> Optional[str]:
        return self._name

    def function_call(self) -> Optional[FunctionCall]:
        return self._function_call

    def usage(self) -> Optional[Usage]:
        return self._usage

    def to_dict(self) -> dict[str, Any]:
        d = {
            ROLE: self._role, 
            CONTENT: self._content
        }
        if self._name is not None:
            d[NAME] = self._name
        if self._function_call is not None:
            d[FUNCTION_CALL] = self._function_call.to_dict()
        return d

    @staticmethod
    def from_result_object(result: dict[str, Any]) -> "ChatformMessage":
        d = result[CHOICES][0][MESSAGE]
        builder = (
            ChatformMessage.Builder()
            .role(d[ROLE])
            .content(d[CONTENT])
            .name(d.get(NAME))
        )
        if FUNCTION_CALL in d:
            builder.function_call(
                ChatformMessage.FunctionCall.Builder()
                .name(d[FUNCTION_CALL][NAME])
                .arguments(d[FUNCTION_CALL][ARGUMENTS])
                .build()
            )
        if USAGE in result:
            builder.usage(
                ChatformMessage.Usage.Builder()
                .completion_tokens(result[USAGE][COMPLETION_TOKENS])
                .prompt_tokens(result[USAGE][PROMPT_TOKENS])
                .build()
            )
        return builder.build()

    def token_size(self, tokeniser: Tokeniser) -> int:
        def size_d(d: dict[Any, Any]) -> int:
            size = 0
            for _, v in d.items():
                if isinstance(v, dict):
                    size += size_d(v) # type: ignore
                else:
                    size += tokeniser.num_tokens(str(v))
            return size

        return size_d(self.to_dict())


def function_call() -> ChatformMessage.FunctionCall.Builder:
    return ChatformMessage.FunctionCall.Builder()


def chatform_message() -> ChatformMessage.Builder:
    return ChatformMessage.Builder()


def user_message(content: str, name: Optional[str] = None) -> ChatformMessage:
    return chatform_message().role(USER).name(name).content(content).build()


def assistant_message(content: str) -> ChatformMessage:
    return chatform_message().role(ASSISTANT).content(content).build()


def system_message(content: str) -> ChatformMessage:
    return chatform_message().role(SYSTEM).content(content).build()


def function_call_message(name: str, arguments: str) -> ChatformMessage:
    return (
        chatform_message()
        .role(FUNCTION)
        .function_call(function_call().name(name).arguments(arguments).build())
        .build()
    )


def function_result_message(name: str, content: str) -> ChatformMessage:
    return chatform_message().role(FUNCTION).name(name).content(content).build()