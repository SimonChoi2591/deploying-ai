"""Offline tests for the embedding and RAG routing."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.router import is_knowledge_query
from services.semantic_embedding import encode, KEYS
from services.rag_service import format_context


class Phase3Tests(unittest.TestCase):
    def test_routing(self):
        self.assertTrue(is_knowledge_query("According to the knowledge base, what is RAG?"))
        self.assertFalse(is_knowledge_query("Explain what RAG is"))

    def test_synonym_embedding(self):
        a = encode("RAG")
        b = encode("retrieval augmented generation")
        self.assertGreater(a[KEYS.index("rag")], 0)
        self.assertGreater(b[KEYS.index("rag")], 0)
        self.assertEqual(len(a), len(KEYS))

    def test_out_of_domain(self):
        self.assertFalse(any(encode("Tell me about the weather tomorrow")))

    def test_context(self):
        self.assertIn("Source 1: Test", format_context([{"title":"Test","text":"Example"}]))


if __name__ == "__main__":
    unittest.main()
