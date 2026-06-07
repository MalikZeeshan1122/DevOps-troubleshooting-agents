import os
from typing import TypeVar

import instructor
from openai import OpenAI
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = "gpt-4o-mini"


class LLMClient:
    """Thin wrapper around OpenAI + instructor for structured agent outputs."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is required. Set it in .env or pass api_key= to LLMClient."
            )

        client_kwargs: dict = {"api_key": api_key}
        base_url = base_url or os.getenv("OPENAI_BASE_URL")
        if base_url:
            client_kwargs["base_url"] = base_url

        self.model = model or os.getenv("LLM_MODEL", DEFAULT_MODEL)
        self._client = instructor.from_openai(OpenAI(**client_kwargs))

    def complete(self, system: str, user: str, response_model: type[T]) -> T:
        return self._client.chat.completions.create(
            model=self.model,
            response_model=response_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
