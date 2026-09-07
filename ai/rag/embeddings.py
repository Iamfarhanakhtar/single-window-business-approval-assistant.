"""
Extensible Embedding Architecture and Vector Representation

Provides the EmbeddingProvider abstraction and a deterministic TF-IDF fallback
allowing zero-API-key local execution with pluggable dense embedding support.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class EmbeddingProvider(ABC):
    """
    Abstract interface for embedding providers.
    Supports pluggable dense embedding models (e.g. sentence-transformers) or local sparse vectors.
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generates an embedding vector for a single query or text."""
        pass

    @abstractmethod
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a list of document strings."""
        pass


class TFIDFEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic local embedding provider using TF-IDF sublinear scaling and n-grams.
    Requires no external API keys and guarantees reproducible cosine similarity scores.
    """

    def __init__(self, ngram_range: Tuple[int, int] = (1, 2)):
        self.ngram_range = ngram_range
        self.vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            sublinear_tf=True,
            strip_accents="unicode",
            lowercase=True,
            stop_words="english",
        )
        self._is_fitted: bool = False
        self._doc_matrix: Optional[Any] = None

    def fit_corpus(self, corpus: List[str]) -> None:
        """Fits the TF-IDF vectorizer vocabulary on the regulatory corpus."""
        if not corpus:
            self._is_fitted = False
            self._doc_matrix = None
            return
        self._doc_matrix = self.vectorizer.fit_transform(corpus)
        self._is_fitted = True

    def embed_text(self, text: str) -> List[float]:
        """Transforms a single query text into an embedding vector."""
        if not self._is_fitted:
            return []
        vec = self.vectorizer.transform([text])
        return vec.toarray()[0].tolist()

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Transforms multiple document texts into embedding vectors."""
        if not self._is_fitted:
            self.fit_corpus(documents)
            return self._doc_matrix.toarray().tolist()
        vecs = self.vectorizer.transform(documents)
        return vecs.toarray().tolist()

    def compute_similarity(self, query: str) -> np.ndarray:
        """Computes cosine similarity between query and all fitted corpus documents."""
        if not self._is_fitted or self._doc_matrix is None:
            return np.array([])
        q_vec = self.vectorizer.transform([query])
        return cosine_similarity(q_vec, self._doc_matrix).flatten()


# Default embedding provider instance (TF-IDF fallback)
default_embedding_provider = TFIDFEmbeddingProvider()
