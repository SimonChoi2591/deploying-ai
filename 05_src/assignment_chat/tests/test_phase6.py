"""End-to-end routing smoke tests with mocked external services."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    import gradio  # noqa: F401
    import dotenv  # noqa: F401
    from app import chat
    HAS_APP = True
except ImportError:
    HAS_APP = False


@unittest.skipUnless(HAS_APP, "Course Gradio/dotenv dependencies unavailable")
class Phase6RoutingTests(unittest.TestCase):
    def test_guardrail_blocks_before_external_calls(self):
        with patch('app.create_client') as client:
            self.assertIn('restricted topic', chat('Tell me about cats', []).lower())
            client.assert_not_called()

    def test_book_service_fallback(self):
        books = [{'title': 'Python Guide', 'authors': ['A. Author'],
                  'year': 2020, 'url': 'https://openlibrary.org/works/OL1W'}]
        with patch('app.search_books', return_value=books), \
             patch('app.create_client', side_effect=RuntimeError('offline')):
            result = chat('Find books about Python', [])
            self.assertIn('Python Guide', result)

    def test_rag_uses_retrieved_context(self):
        hits = [{'title': 'RAG basics', 'text': 'RAG retrieves passages.', 'distance': 0.1}]
        with patch('app.retrieve', return_value=hits), \
             patch('app.create_client', side_effect=RuntimeError('offline')):
            result = chat('According to the knowledge base, what is RAG?', [])
            self.assertIn('RAG basics', result)

    def test_calculator_service_routed(self):
        with patch('app.create_client', return_value=object()), \
             patch('app.answer_with_tools', return_value='Power is 30 W') as tools:
            result = chat('Calculate power at 12V and 2.5A', [])
            self.assertIn('30 W', result)
            tools.assert_called_once()

    def test_general_chat(self):
        from types import SimpleNamespace
        mock_client = SimpleNamespace(responses=SimpleNamespace(create=lambda **kw: SimpleNamespace(output_text='A vector database stores embeddings.')))
        with patch('app.create_client', return_value=mock_client):
            result = chat('What is a vector database?', [])
            self.assertIn('embeddings', result)


if __name__ == '__main__':
    unittest.main()
