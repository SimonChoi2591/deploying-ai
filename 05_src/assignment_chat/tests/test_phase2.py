"""Offline unit tests for Phase 2; no live network or API key required."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.router import extract_book_topic
from services.book_service import search_books, format_books, BookSearchError

class Phase2Tests(unittest.TestCase):
    def test_book_routing(self):
        self.assertIsNotNone(extract_book_topic("Find books about machine learning"))
        self.assertIsNone(extract_book_topic("Explain machine learning"))

    def test_api_parsing(self):
        from io import BytesIO
        payload = b'{"docs":[{"key":"/works/OL1W","title":"Python Basics","author_name":["Jane Doe"],"first_publish_year":2020}]}'
        context = MagicMock()
        context.__enter__.return_value = BytesIO(payload)
        with patch("services.book_service.urlopen", return_value=context):
            books = search_books("python")
        self.assertEqual(books[0]["title"], "Python Basics")
        self.assertEqual(books[0]["url"], "https://openlibrary.org/works/OL1W")
        self.assertIn("Python Basics", format_books(books, "python"))

    def test_api_error(self):
        from urllib.error import URLError
        with patch("services.book_service.urlopen", side_effect=URLError("offline")):
            with self.assertRaises(BookSearchError):
                search_books("python")

if __name__ == "__main__":
    unittest.main()
