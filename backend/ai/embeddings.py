import hashlib
import logging
import math
import re
from typing import List, Union
import numpy as np

from config import Config

logger = logging.getLogger("TMA.Embeddings")


class BaseEmbeddingProvider:
    """Base interface for embedding models in TrekMate AI."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> List[float]:
        raise NotImplementedError

    @property
    def dimension(self) -> int:
        raise NotImplementedError


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, api_key: str, model_name: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model_name = model_name
        self._dim = 1536
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.available = True
        except Exception as e:
            logger.warning(f"OpenAI embedding client initialization failed: {e}")
            self.available = False

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.available or not texts:
            return []
        cleaned_texts = [t.replace("\n", " ") for t in texts]
        res = self.client.embeddings.create(input=cleaned_texts, model=self.model_name)
        return [d.embedding for d in res.data]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    @property
    def dimension(self) -> int:
        return self._dim


class SemanticHashEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic 384-dimensional Dense Semantic Vectorizer.
    Computes dense embeddings from subword n-grams, lexical roots, and domain tokens.
    Guarantees consistent cosine similarity in offline mode without requiring network calls.
    """

    def __init__(self, dim: int = 384):
        self._dim = dim
        self._trek_vocab = {
            "altitude": 10, "mountain": 12, "peak": 14, "himalayas": 16, "summit": 18,
            "pass": 20, "trail": 22, "campsite": 24, "camp": 26, "tent": 28,
            "itinerary": 30, "day": 32, "route": 34, "distance": 36, "elevation": 38,
            "acclimatization": 40, "ams": 42, "oxygen": 44, "diamox": 46, "safety": 48,
            "permit": 50, "forest": 52, "weather": 54, "snow": 56, "rain": 58,
            "gear": 60, "backpack": 62, "boots": 64, "jacket": 66, "poles": 68,
            "fitness": 70, "stamina": 72, "cardio": 74, "beginner": 76, "moderate": 78,
            "difficult": 80, "expert": 82, "guide": 84, "leader": 86, "porter": 88,
            "kedarkantha": 90, "hampta": 92, "roopkund": 94, "har": 96, "chadar": 98,
            "brahmatal": 100, "valley": 102, "flowers": 104, "sandakphu": 106, "goechala": 108,
            "everest": 110, "annapurna": 112, "manali": 114, "rishikesh": 116, "leh": 118,
            "price": 120, "cost": 122, "booking": 124, "slot": 126, "refund": 128
        }

    def _tokenize_and_vectorize(self, text: str) -> List[float]:
        vec = np.zeros(self._dim, dtype=np.float32)
        if not text:
            return vec.tolist()

        words = re.findall(r"\b\w+\b", text.lower())
        if not words:
            return vec.tolist()

        # 1. Domain lexical term matching with semantic weighting
        for w in words:
            if w in self._trek_vocab:
                idx = self._trek_vocab[w] % self._dim
                vec[idx] += 2.5

            # Subword character 3-grams hashing
            for i in range(max(1, len(w) - 2)):
                tri = w[i:i+3]
                h = int(hashlib.md5(tri.encode("utf-8")).hexdigest(), 16)
                idx = h % self._dim
                vec[idx] += 0.4

        # 2. Sequential context hashing
        for i in range(len(words) - 1):
            bigram = f"{words[i]}_{words[i+1]}"
            h = int(hashlib.sha256(bigram.encode("utf-8")).hexdigest(), 16)
            idx = h % self._dim
            vec[idx] += 0.8

        # 3. L2 Unit Normalization (crucial for cosine similarity dot product)
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
        else:
            vec[0] = 1.0

        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._tokenize_and_vectorize(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._tokenize_and_vectorize(text)

    @property
    def dimension(self) -> int:
        return self._dim


def get_embedding_provider() -> BaseEmbeddingProvider:
    """Embedding factory returning configured provider or fast semantic dense fallback."""
    provider_name = Config.EMBEDDING_PROVIDER.lower()
    if provider_name == "openai" and Config.OPENAI_API_KEY:
        try:
            return OpenAIEmbeddingProvider(Config.OPENAI_API_KEY, Config.EMBEDDING_MODEL)
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI Embeddings: {e}. Using SemanticHash fallback.")

    return SemanticHashEmbeddingProvider(dim=384)
