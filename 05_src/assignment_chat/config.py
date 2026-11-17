"""Configuration for TechWise AI using the course's shared OpenAI client."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR.parent

# Load credentials/configuration before importing utils.clients, since its
# USE_GATEWAY default is evaluated at module import time.
load_dotenv(SRC_DIR / ".secrets", override=False)
load_dotenv(SRC_DIR / ".env", override=False)

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from utils.clients import get_client  # noqa: E402

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_HISTORY_TURNS = max(0, int(os.getenv("MAX_HISTORY_TURNS", "8")))
MAX_HISTORY_CHARS = max(0, int(os.getenv("MAX_HISTORY_CHARS", "12000")))


def create_client():
    """Reuse the course client for direct API or gateway access."""
    return get_client()
