import os
from dotenv import load_dotenv

load_dotenv()

PROXY = os.getenv("PROXY")
OPENAI_API_KEY = os.getenv("OPENAI_API")
GEMINI_API_KEY = os.getenv("GEMINI_API")
AI_ASSISTANT_ID = os.getenv("AI_ASSISTANT_ID")


__all__ = [
    "PROXY",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "AI_ASSISTANT_ID",
]
