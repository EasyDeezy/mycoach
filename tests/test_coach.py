import pytest
from unittest.mock import MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from coach import Coach, DEFAULT_SYSTEM_PROMPT


def make_stream_mock(response_chunks: list[str]) -> MagicMock:
    """Create a mock stream context manager that yields the given text chunks."""
    mock_stream = MagicMock()
    mock_stream.text_stream = iter(response_chunks)

    mock_context = MagicMock()
    mock_context.__enter__ = MagicMock(return_value=mock_stream)
    mock_context.__exit__ = MagicMock(return_value=False)
    return mock_context


@pytest.fixture
def mock_client():
    return MagicMock()


class TestCoachInit:
    def test_default_system_prompt(self, mock_client):
        coach = Coach(client=mock_client)
        assert coach.system_prompt == DEFAULT_SYSTEM_PROMPT

    def test_custom_system_prompt(self, mock_client):
        custom_prompt = "You are a fitness coach."
        coach = Coach(client=mock_client, system_prompt=custom_prompt)
        assert coach.system_prompt == custom_prompt

    def test_default_model(self, mock_client):
        coach = Coach(client=mock_client)
        assert coach.model == "claude-opus-4-6"

    def test_custom_model(self, mock_client):
        coach = Coach(client=mock_client, model="claude-haiku-4-5")
        assert coach.model == "claude-haiku-4-5"

    def test_empty_history_on_init(self, mock_client):
        coach = Coach(client=mock_client)
        assert coach.history == []


class TestCoachChat:
    def test_returns_response_text(self, mock_client):
        mock_client.messages.stream.return_value = make_stream_mock(["Great", " goal", "!"])
        coach = Coach(client=mock_client)
        result = coach.chat("I want to run a marathon.")
        assert result == "Great goal!"

    def test_appends_user_message_to_history(self, mock_client):
        mock_client.messages.stream.return_value = make_stream_mock(["Sure!"])
        coach = Coach(client=mock_client)
        coach.chat("My goal is to read 12 books this year.")
        assert coach.history[0] == {
            "role": "user",
            "content": "My goal is to read 12 books this year.",
        }

    def test_appends_assistant_reply_to_history(self, mock_client):
        mock_client.messages.stream.return_value = make_stream_mock(["That's a great goal!"])
        coach = Coach(client=mock_client)
        coach.chat("Help me set a goal.")
        assert coach.history[1] == {
            "role": "assistant",
            "content": "That's a great goal!",
        }

    def test_maintains_conversation_across_turns(self, mock_client):
        mock_client.messages.stream.side_effect = [
            make_stream_mock(["What's your goal?"]),
            make_stream_mock(["Great, let's break that down."]),
        ]
        coach = Coach(client=mock_client)
        coach.chat("I need help.")
        coach.chat("I want to lose weight.")
        assert len(coach.history) == 4

    def test_passes_full_history_to_api(self, mock_client):
        mock_client.messages.stream.side_effect = [
            make_stream_mock(["First response."]),
            make_stream_mock(["Second response."]),
        ]
        coach = Coach(client=mock_client)
        coach.chat("Turn 1")
        coach.chat("Turn 2")

        second_call_messages = mock_client.messages.stream.call_args_list[1].kwargs["messages"]
        assert len(second_call_messages) == 3  # user, assistant, user

    def test_uses_correct_model(self, mock_client):
        mock_client.messages.stream.return_value = make_stream_mock(["Hi!"])
        coach = Coach(client=mock_client, model="claude-haiku-4-5")
        coach.chat("Hello")
        call_kwargs = mock_client.messages.stream.call_args.kwargs
        assert call_kwargs["model"] == "claude-haiku-4-5"

    def test_uses_system_prompt(self, mock_client):
        mock_client.messages.stream.return_value = make_stream_mock(["Hi!"])
        custom_prompt = "Be concise."
        coach = Coach(client=mock_client, system_prompt=custom_prompt)
        coach.chat("Hello")
        call_kwargs = mock_client.messages.stream.call_args.kwargs
        assert call_kwargs["system"] == custom_prompt

    def test_empty_response(self, mock_client):
        mock_client.messages.stream.return_value = make_stream_mock([])
        coach = Coach(client=mock_client)
        result = coach.chat("Hello")
        assert result == ""


class TestCoachReset:
    def test_reset_clears_history(self, mock_client):
        mock_client.messages.stream.return_value = make_stream_mock(["Hi!"])
        coach = Coach(client=mock_client)
        coach.chat("Hello")
        assert len(coach.history) == 2

        coach.reset()
        assert coach.history == []

    def test_can_chat_after_reset(self, mock_client):
        mock_client.messages.stream.side_effect = [
            make_stream_mock(["Before"]),
            make_stream_mock(["After reset"]),
        ]
        coach = Coach(client=mock_client)
        coach.chat("Before reset")
        coach.reset()
        result = coach.chat("Fresh start")
        assert result == "After reset"
        assert len(coach.history) == 2


class TestHistoryProperty:
    def test_history_returns_copy(self, mock_client):
        mock_client.messages.stream.return_value = make_stream_mock(["Hi!"])
        coach = Coach(client=mock_client)
        coach.chat("Hello")
        history = coach.history
        history.clear()
        assert len(coach.history) == 2  # Original unaffected
