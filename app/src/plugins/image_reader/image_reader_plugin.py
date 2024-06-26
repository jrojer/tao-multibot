import json
from typing import Any, Optional
from app.src.butter.checks import check_that
from app.src.gpt.plugin import Plugin
from app.src.internal.common.content_downloader import ContentDownloader
from app.src.internal.image.image import Image
from app.src.observability.logger import Logger
from app.src.gpt.simple_image_text_completer import (
    SimpleImageTextCompleter,
)


logger = Logger(__name__)

# NOTE: This can help for the models that can call function but unable to read images directly
class ImageReaderPlugin(Plugin):
    def __init__(
        self,
        content_downloader: ContentDownloader,
        system_prompt: str,
        openai_token: str,
    ):
        self._content_downloader: ContentDownloader = content_downloader
        self._system_prompt: str = system_prompt
        self._token: str = openai_token

    @staticmethod
    def name() -> str:
        return "image_reader"

    def functions(self) -> list[dict[str, Any]]:
        return [
            {
                "manifest": {
                    "name": "read_image",
                    "description": "Reads an image file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ref": {
                                "type": "string",
                                "description": "image ref",
                            },
                            "prompt": {
                                "type": "string",
                                "description": "Prompt to use for completion",
                            },
                        },
                        "required": ["ref", "prompt"],
                    },
                }
            }
        ]

    async def call(self, name: str, args: str) -> str:
        logger.info("Calling function: %s (%s)", name, args)
        check_that(name == "read_image", "Function name must be 'read_image'")

        d = json.loads(args)
        ref = d["ref"]
        prompt = d["prompt"]

        image: Image = await self._content_downloader.download(ref)

        return await SimpleImageTextCompleter(
            self._system_prompt, self._token
        ).complete(image, prompt)

    def is_delegate(self) -> bool:
        return True
    
    async def system_prompt_attachment(self) -> Optional[str]:
        return None
