from __future__ import annotations
import anthropic
from typing import Optional

DEFAULT_SYSTEM_PROMPT = """You are a supportive personal coach. You help users:
- Set and achieve meaningful goals
- Overcome obstacles and limiting beliefs
- Build positive habits and routines
- Reflect on progress and celebrate wins

Ask clarifying questions to understand the user's situation deeply.
Be encouraging, honest, and action-oriented."""


class Coach:
    def __init__(
        self,
        client: Optional[anthropic.Anthropic] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        model: str = "claude-haiku-4-5",
    ):
        self.client = client or anthropic.Anthropic()
        self.system_prompt = system_prompt
        self.model = model
        self._messages: list[dict] = []

    @property
    def history(self) -> list[dict]:
        return list(self._messages)

    def chat(self, user_message: str) -> str:
        """Send a message to the coach and get a streamed response."""
        self._messages.append({"role": "user", "content": user_message})

        with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            system=self.system_prompt,
            messages=list(self._messages),
        ) as stream:
            response_text = ""
            for text in stream.text_stream:
                print(text, end="", flush=True)
                response_text += text

        print()
        self._messages.append({"role": "assistant", "content": response_text})
        return response_text

    def reset(self) -> None:
        """Clear the conversation history."""
        self._messages = []
