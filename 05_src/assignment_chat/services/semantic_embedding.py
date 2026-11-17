"""Small, deterministic concept embedding; no external embedding service required.

The vectors represent a curated set of technical concepts, not pretrained
semantic embeddings. Synonyms allow limited semantic matching (e.g. RAG and
retrieval augmented generation). The same encoder is used for documents and queries.
"""
import math
import re

CONCEPTS = {'python': ['python', 'programming', 'code', 'script', 'function', 'variable', 'dictionary', 'list'], 'ml': ['machine learning', 'ml', 'training', 'prediction', 'supervised', 'unsupervised', 'model'], 'deep_learning': ['deep learning', 'neural network', 'cnn', 'transformer', 'layers', 'backpropagation'], 'rag': ['rag', 'retrieval augmented generation', 'retrieve', 'grounding', 'knowledge base', 'documents'], 'embeddings': ['embedding', 'vector', 'semantic similarity', 'representation', 'similarity'], 'vector_db': ['vector database', 'chromadb', 'chroma', 'nearest neighbor', 'index', 'vector store'], 'llm': ['llm', 'large language model', 'language model', 'token', 'prompt', 'generation'], 'api': ['api', 'application programming interface', 'endpoint', 'http', 'request', 'response'], 'function_calling': ['function calling', 'tool calling', 'tools', 'function', 'arguments', 'json schema'], 'guardrails': ['guardrails', 'prompt injection', 'safety', 'restricted topics', 'input validation'], 'memory': ['conversation memory', 'chat history', 'context window', 'truncation', 'summarization'], 'evaluation': ['evaluation', 'metrics', 'deepeval', 'accuracy', 'benchmark', 'hallucination'], 'python_types': ['list', 'dictionary', 'tuple', 'set', 'python data structures'], 'classification': ['classification', 'classifier', 'labels', 'precision', 'recall', 'f1'], 'overfitting': ['overfitting', 'generalization', 'regularization', 'validation', 'train test split']}
KEYS = tuple(CONCEPTS)


def encode(text: str, labels=()):
    lowered = (text or "").lower()
    padded = " " + re.sub(r"[^a-z0-9]+", " ", lowered).strip() + " "
    vector = []
    for key in KEYS:
        phrases = CONCEPTS[key]
        count = sum(1 for p in phrases if " " + p.lower() + " " in padded)
        # Explicit document labels supply semantic indexing, even when a
        # document uses a different surface form from the user's question.
        if key in labels:
            count += 3
        vector.append(float(count))
    norm = math.sqrt(sum(x*x for x in vector))
    return [x / norm for x in vector] if norm else [0.0] * len(vector)
