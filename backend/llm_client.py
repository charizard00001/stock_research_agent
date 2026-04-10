import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite")
OCR_MODEL = os.getenv("OPENROUTER_OCR_MODEL", "openai/gpt-4o-mini")
CHAT_MODEL = os.getenv("OPENROUTER_CHAT_MODEL", "google/gemini-3-flash-preview")


def chat(messages: list, system: str = None, stream: bool = False, model: str = None):
    full_messages = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    return client.chat.completions.create(
        model=model or MODEL,
        messages=full_messages,
        stream=stream,
    )


def chat_with_image(image_bytes: bytes, prompt: str, system: str = None):
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{b64}",
                },
            },
        ],
    })

    return client.chat.completions.create(
        model=OCR_MODEL,
        messages=messages,
    )
