"""
Strongly Typed Regulatory RAG Data Models

Defines models for regulatory documents, structured chunks, retrieved evidence,
and citation-grounded answers with provenance tracking.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class SectionItem(BaseModel):
    """Statutory section or clause within a regulatory document."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)
    section_number: str = Field(..., description="Section, Rule, or Schedule identifier")
    title: str = Field(default="", description="Title or description of the section")
    text: str = Field(..., description="Legal provision text")


class RegulatoryDocument(BaseModel):
    """
    Standardized regulatory document model with complete statutory provenance,
    SHA-256 content hashing, and official vs demo classification.
    """
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    document_id: str = Field(..., description="Unique statutory document identifier")
    title: str = Field(..., description="Official title of the Act, Rule, or Regulation")
    source_name: str = Field(..., description="Issuing authority, portal, or gazette name")
    source_url: str = Field(..., description="Verifiable public official URL")
    authority: str = Field(..., description="Governing regulatory board or department")
    jurisdiction: str = Field(..., description="State or Central jurisdiction")
    document_type: str = Field(default="Act", description="Type: Act, Rule, Regulation, Notification, Catalog")
    file_path: Optional[str] = Field(default=None, description="Local file path if loaded from disk")
    retrieved_at: str = Field(..., description="ISO-8601 timestamp when document was captured")
    last_verified_at: str = Field(..., description="ISO-8601 timestamp when document was verified")
    is_official: bool = Field(default=False, description="True if verbatim official gazette; False if demo/synthetic")
    content_hash: str = Field(..., description="SHA-256 digest of normalized document content")
    disclaimer: str = Field(
        default="DEMO / SYNTHETIC — NOT OFFICIAL REGULATORY TEXT",
        description="Statutory warning label"
    )
    raw_text: Optional[str] = Field(default=None, description="Complete raw document text")
    sections: List[SectionItem] = Field(default_factory=list, description="Structured statutory sections")


class DocumentChunk(BaseModel):
    """
    Atomic text segment indexed into the vector store.
    Uses stable naming schema: {document_id}_{chunk_order:04d}
    """
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    chunk_id: str = Field(..., description="Stable chunk identifier (e.g. UP_PCB_WATER_ACT_001_0001)")
    document_id: str = Field(..., description="Parent document identifier")
    document_title: str = Field(..., description="Title of parent statutory document")
    section: str = Field(..., description="Section / Rule reference (e.g. 'Section 25')")
    source_name: str = Field(..., description="Issuing source portal or authority")
    source_url: str = Field(..., description="Official URL reference")
    authority: str = Field(..., description="Regulatory authority")
    jurisdiction: str = Field(..., description="State or Central jurisdiction")
    is_official: bool = Field(default=False, description="Whether from an official gazette")
    text: str = Field(..., description="Text content of the chunk")
    chunk_order: int = Field(default=1, description="Sequential position within parent document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extensible metadata attributes")


class RetrievedChunk(BaseModel):
    """Ranked evidence chunk returned by the retriever."""
    model_config = ConfigDict(from_attributes=True)

    chunk_id: str
    document_id: str
    document_title: str
    section: str
    source_name: str
    source_url: str
    authority: str
    jurisdiction: str
    is_official: bool
    text: str
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0.0 to 1.0)")


class SourceItem(BaseModel):
    """Structured citation item for an answer source."""
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    title: str
    section: str
    source_url: str
    relevance_score: float


class GeneratedAnswer(BaseModel):
    """Final grounded answer produced from retrieved evidence."""
    model_config = ConfigDict(from_attributes=True)

    query: str
    answer: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    sources: List[SourceItem] = Field(default_factory=list)
    evidence_found: bool = Field(default=True)
    requires_verification: bool = Field(default=True)
    evidence: List[str] = Field(default_factory=list)
    verification_notice: str = Field(
        default="Always verify current requirements against the relevant official authority before submission."
    )
