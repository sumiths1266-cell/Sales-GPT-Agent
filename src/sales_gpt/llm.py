from __future__ import annotations

import os

from openai import OpenAI


class SalesLLM:
    def __init__(self, model: str | None = None) -> None:
        self.client = OpenAI()
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5")

    def run(self, *, instructions: str, user_input: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=user_input,
        )
        return response.output_text