"""
Regulatory RAG CLI Demonstration

Demonstrates evidence retrieval, answer generation, source citations,
and strict fallback handling without an external LLM API key.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
curr_path = Path(__file__).resolve().parent
project_root = curr_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ai.rag.pipeline import RegulatoryRAGPipeline


def run_demo():
    print("========================================")
    print("BUSINESS COMPLIANCE HUB")
    print("REGULATORY RAG")
    print("========================================")
    print()

    rag = RegulatoryRAGPipeline()

    sample_queries = [
        ("Why may environmental Consent to Establish (CTE) and Consent to Operate apply to my manufacturing business?", 0.05),
        ("What are the statutory hygiene and licensing prerequisites for food processing under FSSAI?", 0.05),
        ("What is the employee threshold for factory plan approval under Factories Act Section 6?", 0.05),
        ("Why is interplanetary quantum warp drive clearance required for Mars colony exploration?", 0.25),
    ]

    for q, min_thresh in sample_queries:
        print("----------------------------------------------------------------------")
        print(f"Query:\n{q}")
        print()

        result = rag.ask(q, top_k=3, min_score=min_thresh)

        if result["evidence_found"] and result["sources"]:
            print("Retrieved Evidence:")
            for idx, src in enumerate(result["sources"], 1):
                print(f"{idx}. [{src['title']} ({src['section']})] - Relevance: {src['relevance_score']:.2f}")
            print()

            print("Answer:")
            print(result["answer"])
            print()

            print("Sources:")
            for src in result["sources"]:
                print(f"- Document: {src['title']}")
                print(f"  Section: {src['section']}")
                print(f"  Source: {src['source_url']}")
            print()
        else:
            print("Answer:")
            print("INSUFFICIENT_EVIDENCE: No verified statutory regulations were found matching this inquiry.")
            print()

        print("Verification:")
        print("Always verify current requirements against the relevant official authority.")
        print()

    print("========================================")


if __name__ == "__main__":
    run_demo()
