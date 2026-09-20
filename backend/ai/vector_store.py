import json
import logging
import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from config import Config
from ai.embeddings import get_embedding_provider, BaseEmbeddingProvider

logger = logging.getLogger("TMA.VectorStore")


class FAISSVectorStoreManager:
    """
    Manages FAISS vector indexing, metadata persistence, similarity searching,
    and metadata-filtered retrieval for TrekMate AI RAG.
    """

    def __init__(self, index_dir: Optional[str] = None):
        self.index_dir = index_dir or Config.VECTOR_STORE_PATH
        os.makedirs(self.index_dir, exist_ok=True)
        self.index_file = os.path.join(self.index_dir, "faiss_index.bin")
        self.meta_file = os.path.join(self.index_dir, "faiss_metadata.pkl")

        self.embedder: BaseEmbeddingProvider = get_embedding_provider()
        self.dimension: int = self.embedder.dimension
        self.index = None
        self.metadata_store: List[Dict[str, Any]] = []

        self._init_or_load()

    def _init_or_load(self):
        """Loads existing index from disk or creates a new empty one."""
        try:
            import faiss
            self._has_faiss = True
        except ImportError:
            logger.warning("FAISS is not installed. Using pure NumPy in-memory vector search.")
            self._has_faiss = False

        if self._has_faiss and os.path.exists(self.index_file) and os.path.exists(self.meta_file):
            try:
                import faiss
                self.index = faiss.read_index(self.index_file)
                with open(self.meta_file, "rb") as f:
                    self.metadata_store = pickle.load(f)
                logger.info(f"Loaded existing FAISS index with {len(self.metadata_store)} documents.")
                return
            except Exception as e:
                logger.warning(f"Failed to read FAISS index from disk: {e}. Reinitializing.")

        # Initialize fresh index
        if self._has_faiss:
            import faiss
            # IndexFlatIP uses Inner Product (equivalent to Cosine Similarity for normalized vectors)
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            self.vectors = np.empty((0, self.dimension), dtype=np.float32)

        self.metadata_store = []

    def save(self):
        """Persists the FAISS index and metadata store to disk."""
        try:
            if self._has_faiss and self.index is not None:
                import faiss
                faiss.write_index(self.index, self.index_file)
            with open(self.meta_file, "wb") as f:
                pickle.dump(self.metadata_store, f)
            logger.info(f"Successfully saved vector store with {len(self.metadata_store)} chunks.")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Adds a batch of document chunks to the vector index.
        Each chunk dict must contain 'content' and metadata fields.
        """
        if not chunks:
            return 0

        texts = [c["content"] for c in chunks]
        embeddings = self.embedder.embed_documents(texts)
        vectors_np = np.array(embeddings, dtype=np.float32)

        # Ensure L2 normalization for cosine similarity
        norms = np.linalg.norm(vectors_np, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        vectors_np = vectors_np / norms

        if self._has_faiss:
            self.index.add(vectors_np)
        else:
            if hasattr(self, "vectors") and len(self.vectors) > 0:
                self.vectors = np.vstack([self.vectors, vectors_np])
            else:
                self.vectors = vectors_np

        for i, chunk in enumerate(chunks):
            meta = {
                "document_id": chunk.get("document_id"),
                "trek_id": chunk.get("trek_id"),
                "chunk_id": chunk.get("chunk_id", len(self.metadata_store) + i),
                "title": chunk.get("title", "Guide"),
                "page_number": chunk.get("page_number", 1),
                "section_header": chunk.get("section_header", "Overview"),
                "category": chunk.get("category", "route_guide"),
                "content": chunk.get("content", ""),
            }
            self.metadata_store.append(meta)

        self.save()
        return len(chunks)

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        trek_id: Optional[int] = None,
        category: Optional[str] = None,
        score_threshold: float = 0.20,
    ) -> List[Dict[str, Any]]:
        """
        Searches for top-k similar chunks with optional metadata filtering.
        """
        if not self.metadata_store:
            return []

        query_vec = np.array([self.embedder.embed_query(query)], dtype=np.float32)
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm

        results = []

        # Retrieve a broader pool if filtering is applied
        search_k = min(len(self.metadata_store), k * 4 if (trek_id or category) else k)

        if self._has_faiss and self.index is not None and self.index.ntotal > 0:
            scores, indices = self.index.search(query_vec, search_k)
            scores = scores[0]
            indices = indices[0]

            for score, idx in zip(scores, indices):
                if idx < 0 or idx >= len(self.metadata_store):
                    continue
                if score < score_threshold:
                    continue

                meta = self.metadata_store[idx]

                # Metadata Filters
                if trek_id is not None and meta.get("trek_id") is not None and meta["trek_id"] != trek_id:
                    continue
                if category is not None and meta.get("category") != category:
                    continue

                item = dict(meta)
                item["score"] = float(score)
                results.append(item)

                if len(results) >= k:
                    break
        else:
            # Fallback pure NumPy cosine similarity
            if hasattr(self, "vectors") and len(self.vectors) > 0:
                dots = np.dot(self.vectors, query_vec.T).squeeze()
                sorted_idx = np.argsort(-dots)
                for idx in sorted_idx:
                    score = float(dots[idx])
                    if score < score_threshold:
                        continue
                    meta = self.metadata_store[idx]
                    if trek_id is not None and meta.get("trek_id") is not None and meta["trek_id"] != trek_id:
                        continue
                    if category is not None and meta.get("category") != category:
                        continue
                    item = dict(meta)
                    item["score"] = score
                    results.append(item)
                    if len(results) >= k:
                        break

        return results

    def clear_index(self):
        """Clears all vectors and metadata."""
        if self._has_faiss:
            import faiss
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            self.vectors = np.empty((0, self.dimension), dtype=np.float32)
        self.metadata_store = []
        self.save()


# Singleton instance
_vector_store_instance = None


def get_vector_store() -> FAISSVectorStoreManager:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = FAISSVectorStoreManager()
    return _vector_store_instance
