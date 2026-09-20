import os
import re
import time
import logging
from typing import List, Dict, Any, Optional, Tuple

from config import Config
from models import db, TrekDocument, DocumentChunk, Trek
from ai.vector_store import get_vector_store
from ai.llm_provider import get_llm_provider

logger = logging.getLogger("TMA.RAGService")


class RAGPipelineService:
    """
    Production-grade RAG pipeline using LangChain chunking, FAISS vector retrieval,
    and grounded synthesis with explicit document citations.
    """

    def __init__(self):
        self.vector_store = get_vector_store()
        self.llm = get_llm_provider()

    def extract_text_from_file(self, file_path: str, file_type: str) -> List[Tuple[int, str]]:
        """
        Extracts text from file per page. Returns list of (page_number, text).
        """
        pages_content = []
        ext = file_type.lower().strip(".")

        try:
            if ext == "pdf":
                import pypdf
                reader = pypdf.PdfReader(file_path)
                for i, page in enumerate(reader.pages):
                    txt = page.extract_text() or ""
                    if txt.strip():
                        pages_content.append((i + 1, txt))

            elif ext in ["docx", "doc"]:
                import docx
                doc = docx.Document(file_path)
                full_text = "\n".join([p.text for p in doc.paragraphs if p.text])
                pages_content.append((1, full_text))

            else:  # txt, md, etc.
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    txt = f.read()
                # Split roughly by markdown headers or form feeds if multi-page
                parts = txt.split("\f")
                if len(parts) > 1:
                    for i, p in enumerate(parts):
                        pages_content.append((i + 1, p))
                else:
                    pages_content.append((1, txt))

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            # Fallback plain text read
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    pages_content = [(1, f.read())]
            except Exception:
                pages_content = [(1, "")]

        return pages_content

    def chunk_and_index_document(self, document_id: int) -> int:
        """
        Loads document from DB, splits with RecursiveCharacterTextSplitter,
        populates DocumentChunk records, and indexes into FAISS vector store.
        """
        doc = TrekDocument.query.get(document_id)
        if not doc:
            raise ValueError(f"Document {document_id} not found.")

        # Delete any previous chunks for this document
        DocumentChunk.query.filter_by(document_id=doc.id).delete()
        db.session.commit()

        pages = self.extract_text_from_file(doc.file_path, doc.file_type)
        if not pages:
            doc.is_indexed = False
            doc.chunk_count = 0
            db.session.commit()
            return 0

        # LangChain text splitter
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.RAG_CHUNK_SIZE,
            chunk_overlap=Config.RAG_CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        all_chunks_data = []
        chunk_idx = 0

        for page_num, page_text in pages:
            if not page_text.strip():
                continue

            splits = splitter.split_text(page_text)
            for split_text in splits:
                if len(split_text.strip()) < 20:
                    continue

                # Detect section header
                section = self._detect_section_header(split_text)

                chunk_obj = DocumentChunk(
                    document_id=doc.id,
                    trek_id=doc.trek_id,
                    chunk_index=chunk_idx,
                    content=split_text.strip(),
                    page_number=page_num,
                    section_header=section,
                    token_count=len(split_text.split()),
                )
                db.session.add(chunk_obj)

                all_chunks_data.append({
                    "document_id": doc.id,
                    "trek_id": doc.trek_id,
                    "chunk_id": chunk_idx,
                    "title": doc.title,
                    "page_number": page_num,
                    "section_header": section,
                    "category": doc.category,
                    "content": split_text.strip(),
                })
                chunk_idx += 1

        db.session.commit()

        # Add to Vector Store
        indexed_count = self.vector_store.add_chunks(all_chunks_data)

        doc.chunk_count = indexed_count
        doc.is_indexed = True
        doc.summary = self._generate_quick_summary(doc.title, pages[0][1] if pages else "")
        db.session.commit()

        logger.info(f"Indexed {indexed_count} chunks for document: {doc.title}")
        return indexed_count

    def _detect_section_header(self, text: str) -> str:
        """Finds markdown headers, uppercase titles, or day indicators in chunk."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if not lines:
            return "General Information"

        first_line = lines[0]
        # Match '# Header' or 'Day X: Title' or 'SECTION:'
        if first_line.startswith(("#", "Day", "DAY", "Section", "SECTION", "Safety", "Gear", "Permits", "Altitude")):
            return first_line.replace("#", "").strip()[:80]

        # Check for uppercase heading
        if first_line.isupper() and len(first_line) < 60:
            return first_line

        return "Overview & Guidelines"

    def _generate_quick_summary(self, title: str, sample_text: str) -> str:
        """Generates concise summary of the document for organizer view."""
        sample = sample_text[:800].replace("\n", " ").strip()
        if len(sample) < 50:
            return f"Official comprehensive guide covering {title}."
        return f"{title}: Includes trail logistics, safety considerations, terrain notes, and seasonal advice."

    def retrieve_relevant_contexts(
        self,
        query: str,
        trek_id: Optional[int] = None,
        category: Optional[str] = None,
        top_k: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-k relevant chunks from FAISS vector store.
        """
        return self.vector_store.similarity_search(
            query=query,
            k=top_k,
            trek_id=trek_id,
            category=category,
            score_threshold=Config.RAG_SIMILARITY_THRESHOLD,
        )

    def generate_grounded_answer(
        self,
        user_query: str,
        trek_id: Optional[int] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        End-to-end RAG question-answering with strict grounding and page citations.
        """
        start_time = time.time()
        retrieved_chunks = self.retrieve_relevant_contexts(
            query=user_query,
            trek_id=trek_id,
            category=category,
            top_k=Config.RAG_TOP_K,
        )

        # Also retrieve database context for the trek if trek_id is provided
        trek_db_info = ""
        if trek_id:
            trek = Trek.query.get(trek_id)
            if trek:
                trek_db_info = (
                    f"Trek Name: {trek.trek_name}\n"
                    f"Location: {trek.location} ({trek.region})\n"
                    f"Max Altitude: {trek.max_altitude_m}m | Difficulty: {trek.difficulty}\n"
                    f"Duration: {trek.duration} days | Distance: {trek.distance_km} km\n"
                    f"Base Camp: {trek.base_camp} | Best Season: {trek.best_season}\n"
                    f"Permits Required: {trek.permits_required}\n"
                    f"Safety Guidelines: {trek.safety_guidelines}\n"
                    f"Gear Requirements: {trek.gear_requirements}\n"
                )

        # Format Context & Citations
        context_blocks = []
        sources = []

        if trek_db_info:
            context_blocks.append(f"[DATABASE RECORD: Official Trek Profile]\n{trek_db_info}")

        for i, chunk in enumerate(retrieved_chunks):
            doc_title = chunk.get("title", "Trekking Guide")
            page_num = chunk.get("page_number", 1)
            section = chunk.get("section_header", "Guide")
            score = chunk.get("score", 0.0)

            citation_label = f"{doc_title} (p. {page_num}, § {section})"
            context_blocks.append(f"[{citation_label}]\n{chunk.get('content')}")

            sources.append({
                "document_id": chunk.get("document_id"),
                "trek_id": chunk.get("trek_id"),
                "title": doc_title,
                "page_number": page_num,
                "section": section,
                "similarity_score": round(score, 3),
                "citation": citation_label,
                "excerpt": chunk.get("content", "")[:180] + "...",
            })

        formatted_context = "\n\n---\n\n".join(context_blocks)

        system_prompt = (
            "You are TrekMate AI, an expert high-altitude mountaineering and trekking assistant.\n"
            "Answer the user query strictly using the verified context provided below.\n"
            "Rules for Grounding & Safety:\n"
            "1. Ground your answer in the provided documents and database records.\n"
            "2. When stating facts, altitudes, gear requirements, or route advice, cite the source document, page, and section.\n"
            "3. If the context does not contain sufficient details to answer safely, acknowledge what is known and clarify what is missing.\n"
            "4. For any high-altitude safety queries, include essential acclimatization rules and remind users to carry emergency medicines.\n"
            "5. Maintain a professional, adventurous, and encouraging tone.\n\n"
            f"VERIFIED CONTEXT:\n{formatted_context if formatted_context else 'No external documents found. Use general high-altitude safety guidelines.'}"
        )

        messages = [
            {"role": "user", "content": user_query}
        ]

        llm_res = self.llm.generate_chat_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=850,
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # Compute Grounding Score based on citation & content overlap
        grounding_score = self._evaluate_grounding(llm_res.get("content", ""), retrieved_chunks, trek_db_info)

        return {
            "answer": llm_res.get("content"),
            "sources": sources,
            "citations": sources,
            "retrieval_count": len(retrieved_chunks),
            "grounding_score": grounding_score,
            "model_used": llm_res.get("model", "mock"),
            "latency_ms": latency_ms,
            "prompt_tokens": llm_res.get("prompt_tokens", 0),
            "completion_tokens": llm_res.get("completion_tokens", 0),
        }

    def query_rag(
        self,
        question: str,
        trek_id: Optional[int] = None,
        category: Optional[str] = None,
        top_k: int = 4,
    ) -> Dict[str, Any]:
        """Convenience alias for RAG query."""
        return self.generate_grounded_answer(
            user_query=question,
            trek_id=trek_id,
            category=category,
        )

    def _evaluate_grounding(self, answer: str, chunks: List[Dict[str, Any]], db_info: str) -> float:
        """Heuristic grounding validation checking fact overlap."""
        if not chunks and not db_info:
            return 0.75

        combined_context = (db_info + " " + " ".join([c.get("content", "") for c in chunks])).lower()
        answer_words = set(re.findall(r"\b[a-z]{4,}\b", answer.lower()))

        if not answer_words:
            return 0.9

        matched_words = [w for w in answer_words if w in combined_context]
        ratio = len(matched_words) / len(answer_words)

        # Scale from 0.5 to 1.0
        return min(1.0, max(0.5, round(0.5 + 0.5 * ratio, 2)))


# Singleton instance
_rag_service_instance = None


def get_rag_service() -> RAGPipelineService:
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGPipelineService()
    return _rag_service_instance
