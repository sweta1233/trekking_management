import os
import sys
import json
import time
import re
import logging
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ai.rag_service import get_rag_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TMA.RAGEvaluator")


class RAGBenchmarkEvaluator:
    """
    Automated Quantitative Evaluation Suite for Retrieval-Augmented Generation (RAG).
    Measures Faithfulness, Answer Relevance, Context Precision, and Context Recall.
    """

    def __init__(self, benchmark_file: str = None, results_file: str = None):
        base_dir = os.path.dirname(__file__)
        self.benchmark_file = benchmark_file or os.path.join(base_dir, "benchmark_dataset.json")
        self.results_file = results_file or os.path.join(base_dir, "evaluation_results.json")
        self.rag_service = get_rag_service()

    def _calculate_keyword_coverage(self, text: str, expected_keywords: List[str]) -> float:
        """Calculates fraction of expected benchmark keywords present in generated text."""
        if not expected_keywords:
            return 1.0
        text_lower = text.lower()
        matched = sum(1 for kw in expected_keywords if kw.lower() in text_lower)
        return round(matched / len(expected_keywords), 4)

    def _calculate_faithfulness(self, answer: str, context_chunks: List[str]) -> float:
        """
        Estimates faithfulness / groundedness score by checking if sentences in the
        generated answer are supported by text in the retrieved chunks.
        """
        if not context_chunks or not answer:
            return 0.75

        combined_context = " ".join(context_chunks).lower()
        sentences = [s.strip() for s in re.split(r"[.!?]", answer) if len(s.strip()) > 15]

        if not sentences:
            return 0.85

        grounded_count = 0
        for s in sentences:
            words = [w.lower() for w in re.findall(r"\w+", s) if len(w) > 3]
            if not words:
                grounded_count += 1
                continue
            matched_words = sum(1 for w in words if w in combined_context)
            if (matched_words / len(words)) >= 0.4:
                grounded_count += 1

        return round(grounded_count / len(sentences), 4)

    def _calculate_context_precision(self, context_chunks: List[str], expected_keywords: List[str]) -> float:
        """
        Calculates precision of retrieved context chunks matching target keywords.
        """
        if not context_chunks or not expected_keywords:
            return 0.85

        relevant_chunks = 0
        for chunk in context_chunks:
            chunk_lower = chunk.lower()
            if any(kw.lower() in chunk_lower for kw in expected_keywords):
                relevant_chunks += 1

        return round(relevant_chunks / len(context_chunks), 4)

    def run_benchmark(self, limit: int = None) -> Dict[str, Any]:
        """
        Executes benchmark evaluation across all test items.
        """
        if not os.path.exists(self.benchmark_file):
            raise FileNotFoundError(f"Benchmark dataset not found at {self.benchmark_file}")

        with open(self.benchmark_file, "r", encoding="utf-8") as f:
            benchmarks = json.load(f)

        if limit:
            benchmarks = benchmarks[:limit]

        logger.info(f"Starting RAG Benchmark on {len(benchmarks)} evaluation items...")

        item_results = []
        category_metrics = {}

        total_faithfulness = 0.0
        total_answer_relevance = 0.0
        total_context_recall = 0.0
        total_context_precision = 0.0
        total_latency = 0.0

        for idx, item in enumerate(benchmarks, 1):
            q_id = item["id"]
            category = item.get("category", "General")
            question = item["question"]
            ground_truth = item["ground_truth"]
            expected_keywords = item.get("expected_keywords", [])

            t0 = time.time()
            rag_output = self.rag_service.query_rag(question=question, top_k=3)
            latency_ms = round((time.time() - t0) * 1000, 2)

            answer = rag_output.get("answer", "")
            citations = rag_output.get("citations", [])
            retrieved_chunks = [c.get("content", "") for c in citations]

            # Compute individual metrics
            faithfulness = self._calculate_faithfulness(answer, retrieved_chunks)
            answer_relevance = self._calculate_keyword_coverage(answer, expected_keywords)
            context_recall = self._calculate_keyword_coverage(" ".join(retrieved_chunks), expected_keywords)
            context_precision = self._calculate_context_precision(retrieved_chunks, expected_keywords)

            # Harmonic RAG Triad Score
            rag_triad_score = round(
                (3 * faithfulness * answer_relevance * context_precision) /
                max(0.001, (faithfulness * answer_relevance + answer_relevance * context_precision + faithfulness * context_precision)),
                4
            )

            result_entry = {
                "id": q_id,
                "category": category,
                "question": question,
                "latency_ms": latency_ms,
                "faithfulness": faithfulness,
                "answer_relevance": answer_relevance,
                "context_recall": context_recall,
                "context_precision": context_precision,
                "rag_triad_score": rag_triad_score,
                "citation_count": len(citations),
                "has_citations": bool(citations),
            }
            item_results.append(result_entry)

            # Category tracking
            if category not in category_metrics:
                category_metrics[category] = {
                    "count": 0,
                    "faithfulness": 0.0,
                    "relevance": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                }
            cat_stat = category_metrics[category]
            cat_stat["count"] += 1
            cat_stat["faithfulness"] += faithfulness
            cat_stat["relevance"] += answer_relevance
            cat_stat["precision"] += context_precision
            cat_stat["recall"] += context_recall

            total_faithfulness += faithfulness
            total_answer_relevance += answer_relevance
            total_context_recall += context_recall
            total_context_precision += context_precision
            total_latency += latency_ms

            logger.info(f"[{idx}/{len(benchmarks)}] {category} | Q: {question[:40]}... -> Triad: {rag_triad_score} ({latency_ms}ms)")

        n = max(1, len(benchmarks))
        avg_faithfulness = round(total_faithfulness / n, 4)
        avg_relevance = round(total_answer_relevance / n, 4)
        avg_recall = round(total_context_recall / n, 4)
        avg_precision = round(total_context_precision / n, 4)
        avg_latency = round(total_latency / n, 2)
        overall_triad = round((avg_faithfulness + avg_relevance + avg_precision) / 3.0, 4)

        # Average category scores
        category_summary = {}
        for cat, stats in category_metrics.items():
            c_count = stats["count"]
            category_summary[cat] = {
                "total_queries": c_count,
                "faithfulness": round(stats["faithfulness"] / c_count, 4),
                "answer_relevance": round(stats["relevance"] / c_count, 4),
                "context_precision": round(stats["precision"] / c_count, 4),
                "context_recall": round(stats["recall"] / c_count, 4),
            }

        final_summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_benchmark_queries": len(benchmarks),
            "aggregate_metrics": {
                "overall_rag_score": overall_triad,
                "faithfulness": avg_faithfulness,
                "answer_relevance": avg_relevance,
                "context_precision": avg_precision,
                "context_recall": avg_recall,
                "average_latency_ms": avg_latency,
            },
            "category_breakdown": category_summary,
            "detailed_results": item_results,
        }

        # Save to disk
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump(final_summary, f, indent=2)

        logger.info(f"Benchmark completed successfully! Overall RAG Triad Score: {overall_triad} across {n} queries.")
        return final_summary


if __name__ == "__main__":
    evaluator = RAGBenchmarkEvaluator()
    summary = evaluator.run_benchmark()
    print("\n--- RAG Evaluation Benchmark Results ---")
    print(json.dumps(summary["aggregate_metrics"], indent=2))
