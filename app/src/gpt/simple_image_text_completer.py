import aiohttp
from typing import Any, Optional

from app.src.butter.checks import check_optional
from app.src.internal.image.image import Image


class SimpleImageTextCompleter:
    def __init__(self, system_prompt: str, token: str) -> None:
        self._system_prompt = system_prompt
        self._token = token

    async def complete(
        self, input: str | Image, image_prompt: Optional[str] = None
    ) -> str:
        if type(input) is Image:
            obj = [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{input.as_base64()}"},
                }
            ]
            if image_prompt is not None:
                check_optional(image_prompt, "image_prompt", str)
                obj.append({"type": "text", "text": image_prompt})
            return await self._complete(obj)
        elif type(input) is str:
            return await self._complete([{"type": "text", "text": input}])
        else:
            raise RuntimeError(f"Invalid input type: {type(input)}")

    async def _complete(self, complete_object: list[dict[str, Any]]) -> str:
        data = await _async_post(
            url="https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-4o",
                "max_tokens": 4000,
                "temperature": 0,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "messages": [
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": self._system_prompt}],
                    },
                    {"role": "user", "content": complete_object},
                ],
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._token}",
            },
        )
        return data["choices"][0]["message"]["content"]


async def _async_post(
    url: str, json: dict[str, Any], headers: dict[str, str]
) -> dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
