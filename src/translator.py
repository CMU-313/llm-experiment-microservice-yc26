import os
from typing import Any
from ollama import Client

# 1. Initialize the Ollama Client
OLLAMA_URL = os.getenv("OLLAMA_HOST", "localhost:11434")
client = Client(host=OLLAMA_URL)
MODEL_NAME = "qwen3:0.6b"


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
You are a language detector and translator.
Step 1: Is the post written in English? Answer Yes or No.
Step 2: If not English, translate to English. If English, keep as-is.

Reply in this format:
ENGLISH: <answer>
TEXT: <translated text>""".strip()

    try:
        # 2. Call the local Ollama model
        response = client.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": content}
            ]
        )

        # 3. Robust Error Handling & Parsing
        output = _extract_message_content(response)
        if output is None:
            return (True, content)

        # Clean /think artifacts from output
        output = output.replace("/think", "").strip()

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

        # Fallback: if model returned raw Yes/No + text without prefixes
        if english_value is None and len(lines) >= 2:
            if lines[0].strip().lower() in {"yes", "no"}:
                english_value = lines[0].strip().lower()
                text_value = lines[1].strip()

        if text_value is None or text_value.strip() == "":
            return (True, content)

        # Heuristic: if translation differs from input, it's not English
        if english_value == "yes" and text_value.lower() != content.lower():
            english_value = "no"

        if english_value not in {"yes", "no"}:
            return (True, content)

        is_english = (english_value == "yes")
        return (is_english, text_value)

    except Exception as e:
        # 4. Ultimate Fallback: If anything crashes, return the original text
        print(f"Translation API Error: {e}")
        return (True, content)