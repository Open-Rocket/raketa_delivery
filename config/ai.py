from dependencies._dependencies import os, load_dotenv

load_dotenv()

PROXY = os.getenv("PROXY")
OPENAI_API_KEY = os.getenv("OPENAI_API")
AI_ASSISTANT_ID = os.getenv("AI_ASSISTANT_ID")


__all__ = ["PROXY", "OPENAI_API_KEY", "AI_ASSISTANT_ID"]
