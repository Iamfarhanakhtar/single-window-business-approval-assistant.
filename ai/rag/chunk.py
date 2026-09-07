"""
Deterministic Legal Document Chunking Strategy

Preserves document identity, statutory headings, source provenance, and chunk sequence
with stable IDs formatted as {document_id}_{chunk_order:04d}.
"""

from typing import List
from ai.rag.models import RegulatoryDocument, DocumentChunk


def chunk_regulatory_document(
    doc: RegulatoryDocument,
    max_chunk_words: int = 250,
    overlap_words: int = 40
) -> List[DocumentChunk]:
    """
    Splits a RegulatoryDocument into atomic, semantically coherent chunks
    with stable IDs and propagated statutory provenance.
    """
    chunks: List[DocumentChunk] = []
    chunk_counter = 1

    for sec in doc.sections:
        words = sec.text.strip().split()
        if not words:
            continue

        sec_ref = sec.section_number
        if sec.title and sec.title.lower() != sec.section_number.lower():
            sec_ref = f"{sec.section_number} - {sec.title}"

        if len(words) <= max_chunk_words:
            chunk_id = f"{doc.document_id}_{chunk_counter:04d}"
            chunk_text = f"[{doc.title}] {sec_ref}: {sec.text.strip()}"

            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=doc.document_id,
                document_title=doc.title,
                section=sec.section_number,
                source_name=doc.source_name,
                source_url=doc.source_url,
                authority=doc.authority,
                jurisdiction=doc.jurisdiction,
                is_official=doc.is_official,
                text=chunk_text,
                chunk_order=chunk_counter,
                metadata={
                    "section_title": sec.title,
                    "authority": doc.authority,
                    "jurisdiction": doc.jurisdiction,
                    "source_url": doc.source_url,
                    "document_type": doc.document_type,
                }
            )
            chunks.append(chunk)
            chunk_counter += 1
        else:
            # Sliding window splitting for long sections
            start = 0
            sub_part = 1
            while start < len(words):
                end = min(start + max_chunk_words, len(words))
                sub_words = words[start:end]
                sub_text = " ".join(sub_words)

                chunk_id = f"{doc.document_id}_{chunk_counter:04d}"
                chunk_text = f"[{doc.title}] {sec_ref} (Part {sub_part}): {sub_text}"

                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=doc.document_id,
                    document_title=doc.title,
                    section=f"{sec.section_number} (Part {sub_part})",
                    source_name=doc.source_name,
                    source_url=doc.source_url,
                    authority=doc.authority,
                    jurisdiction=doc.jurisdiction,
                    is_official=doc.is_official,
                    text=chunk_text,
                    chunk_order=chunk_counter,
                    metadata={
                        "section_title": sec.title,
                        "part": sub_part,
                        "authority": doc.authority,
                        "jurisdiction": doc.jurisdiction,
                        "source_url": doc.source_url,
                        "document_type": doc.document_type,
                    }
                )
                chunks.append(chunk)
                chunk_counter += 1
                sub_part += 1

                if end == len(words):
                    break
                start += max_chunk_words - overlap_words

    return chunks


def chunk_all_documents(documents: List[RegulatoryDocument]) -> List[DocumentChunk]:
    """Chunks an entire list of RegulatoryDocuments."""
    all_chunks: List[DocumentChunk] = []
    for doc in documents:
        all_chunks.extend(chunk_regulatory_document(doc))
    return all_chunks
