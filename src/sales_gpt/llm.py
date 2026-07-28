from __future__ import annotations

import os
from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class SalesLLM:
    def __init__(self, model: str | None = None) -> None:
        self.client = OpenAI()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5")

    def run(self, *, instructions: str, user_input: str, web_search: bool = False) -> str:
        kwargs = {
            "model": self.model,
            "instructions": instructions,
            "input": user_input,
        }
        if web_search:
            kwargs["tools"] = [{"type": "web_search_preview"}]
        response = self.client.responses.create(**kwargs)
        return response.output_text

    def run_structured(
        self,
        *,
        instructions: str,
        user_input: str,
        schema: type[T],
        web_search: bool = False,
    ) -> T:
        kwargs = {
            "model": self.model,
            "instructions": instructions,
            "input": user_input,
            "text_format": schema,
        }
        if web_search:
            kwargs["tools"] = [{"type": "web_search_preview"}]
        response = self.client.responses.parse(**kwargs)
        if response.output_parsed is None:
            raise RuntimeError("Model returned no structured result")
        return response.output_parsed