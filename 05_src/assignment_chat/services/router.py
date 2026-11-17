"""Deterministic book-intent detection; general chat remains unchanged."""
import re

BOOK_INTENT = re.compile(
    r"\b(?:books?|textbooks?|reading list|reading recommendations?)\b", re.I
)
BOOK_VERB = re.compile(
    r"\b(?:find|search|recommend|suggest|list|show|looking for|looking to read)\b", re.I
)
TOPIC_PREFIX = re.compile(
    r"^(?:please\s+)?(?:find|search for|recommend|suggest|list|show me)\s+", re.I
)


def extract_book_topic(message: str) -> str | None:
    """Return query for clear book-search intent, otherwise None."""
    if not BOOK_INTENT.search(message) or not BOOK_VERB.search(message):
        return None
    query = TOPIC_PREFIX.sub("", message.strip())
    query = re.sub(r"\b(?:some|a few|the best|good|beginner-friendly)\b", " ", query, flags=re.I)
    query = re.sub(r"\b(?:books?|textbooks?|reading list|reading recommendations?)\b", " ", query, flags=re.I)
    query = re.sub(r"\b(?:about|on|for|related to|please|me)\b", " ", query, flags=re.I)
    query = re.sub(r"\s+", " ", query).strip(" .?!")
    return query or "technology"


# Route explicit knowledge-base requests to Service 2. General questions
# remain normal chat so users can compare grounded and general responses.
import re as _re
_RAG = _re.compile(r"\b(?:knowledge base|knowledge-base|search (?:the )?documents|"
                   r"according to (?:the )?(?:documents|knowledge base)|"
                   r"from (?:the )?(?:documents|knowledge base))\b", _re.I)


def is_knowledge_query(message: str) -> bool:
    return bool(_RAG.search(message))
