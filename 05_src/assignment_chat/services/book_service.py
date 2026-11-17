"""Open Library search service: returns structured records, not raw API text."""
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

API_URL = "https://openlibrary.org/search.json"

class BookSearchError(Exception):
    """Raised when the public book API cannot provide usable results."""


def search_books(topic: str, limit: int = 5) -> list[dict]:
    """Search Open Library. Only a small allowlist of fields is returned."""
    topic = topic.strip()
    if not topic:
        raise ValueError("Please specify a book topic.")
    limit = max(1, min(int(limit), 5))
    params = urlencode({"q": topic, "limit": limit,
                        "fields": "key,title,author_name,first_publish_year,edition_count"})
    req = Request(API_URL + "?" + params,
                  headers={"User-Agent": "TechWiseAI-EducationalProject/1.0 (book search)",
                           "Accept": "application/json"})
    try:
        with urlopen(req, timeout=12) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        raise BookSearchError("The Open Library service is currently unavailable.") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("docs"), list):
        raise BookSearchError("The book service returned an unexpected response.")
    books = []
    for item in payload["docs"][:limit]:
        if not isinstance(item, dict):
            continue
        key = item.get("key", "")
        if not isinstance(key, str) or not key.startswith("/works/"):
            key = ""
        authors = item.get("author_name", [])
        if not isinstance(authors, list):
            authors = []
        books.append({
            "title": str(item.get("title") or "Untitled")[:200],
            "authors": [str(x)[:100] for x in authors[:3]],
            "first_publish_year": item.get("first_publish_year") if isinstance(item.get("first_publish_year"), int) else None,
            "edition_count": item.get("edition_count") if isinstance(item.get("edition_count"), int) else None,
            "url": "https://openlibrary.org" + key if key else None,
        })
    return books


def format_books(books: list[dict], topic: str) -> str:
    """Deterministic natural-language fallback, also useful when LLM fails."""
    if not books:
        return f"I couldn't find books matching {topic!r} in Open Library. Try a broader topic."
    lines = [f"I found {len(books)} Open Library results for {topic!r}:"]
    for idx, book in enumerate(books, 1):
        author = ", ".join(book["authors"]) or "author not listed"
        year = str(book["first_publish_year"]) if book["first_publish_year"] else "year not listed"
        line = f"{idx}. {book['title']} — {author} (first published: {year})."
        if book.get("url"):
            line += " " + book["url"]
        lines.append(line)
    lines.append("These are search results, not independently verified recommendations.")
    return "\n".join(lines)
