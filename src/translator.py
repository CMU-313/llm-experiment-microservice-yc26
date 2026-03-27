import os
from typing import Any

from ollama import Client

# 1. Initialize the Ollama Client
OLLAMA_URL = os.getenv("OLLAMA_HOST", "localhost:11434")
client = Client(host=OLLAMA_URL)
MODEL_NAME = "llama3.1"


def _extract_message_content(response: Any) -> str | None:
    """Extract assistant text from either dict-like or object-like responses."""
    if response is None:
        return None

    if isinstance(response, dict):
        message = response.get("message")
    else:
        message = getattr(response, "message", None)

    if message is None:
        return None

    if isinstance(message, dict):
        content = message.get("content")
    else:
        content = getattr(message, "content", None)

    if not isinstance(content, str):
        return None

    return content


def translate(content: str) -> tuple[bool, str]:
    """
    Robustly queries the model and validates that the response follows
    the expected format. If the response is malformed or an error occurs, 
    returns a safe fallback so NodeBB can continue functioning.
    """
    
    context = """/no_think
You are helping moderate NodeBB posts.

Task:
1. Determine if the post is written in English.
2. If it is English, return the original text unchanged.
3. If it is not English, translate it into fluent English.

Important:
- If the post is not in English, TEXT must be the English translation, not the original text.
- Never copy the original non-English text into TEXT unless it is already English.

Return EXACTLY in this format:

ENGLISH: Yes or No
TEXT: <text>

Do not include anything else.
""".strip()

    try:
        # 2. Call the local Ollama model
        response = client.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": content}
            ]
        )

        # 3. Robust Error Handling & Parsing (Written by your team)
        output = _extract_message_content(response)
        if output is None:
            return (True, content)

        output = output.strip()
        if output == "":
            return (True, content)

        lines = [line.strip() for line in output.splitlines() if line.strip()]

        english_value = None
        text_value = None

        for line in lines:
            lower = line.lower()
            if lower.startswith("english:"):
                english_value = line.split(":", 1)[1].strip().lower()
            elif lower.startswith("text:"):
                text_value = line.split(":", 1)[1].strip()

        if english_value not in {"yes", "no"}:
            return (True, content)

        if text_value is None or text_value.strip() == "":
            return (True, content)

        is_english = (english_value == "yes")
        return (is_english, text_value)

    except Exception as e:
        # 4. Ultimate Fallback: If anything crashes, return the original text
        print(f"Translation API Error: {e}")
        return (True, content)