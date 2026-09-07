"""
Regulatory Document Ingestion and Provenance Tracking

Discovers and parses local regulatory files (.json, .md, .txt) and CSV catalogs,
generates stable SHA-256 hashes, detects duplicates, and builds RegulatoryDocument objects.
"""

import os
import re
import json
import csv
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set

from ai.rag.models import RegulatoryDocument, SectionItem


def compute_content_hash(text: str) -> str:
    """Computes a deterministic SHA-256 digest of normalized text."""
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def normalize_text(text: str) -> str:
    """Normalizes whitespace and standardizes line breaks."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join([l for l in lines if l])


class RegulatoryDataIngester:
    """
    Discovers, ingests, and normalizes statutory regulatory documents.
    """

    def __init__(self, regulations_dir: Optional[str] = None, csv_path: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent / "regulatory_data"
        self.regulations_dir = Path(regulations_dir) if regulations_dir else base_dir / "regulations"
        self.csv_path = Path(csv_path) if csv_path else base_dir / "approvals.csv"
        self._seen_hashes: Set[str] = set()
        self._seen_doc_ids: Set[str] = set()

    def _parse_json_document(self, file_path: Path) -> Optional[RegulatoryDocument]:
        """Parses a structured JSON regulation document."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_content = json.dumps(data, sort_keys=True)
        content_hash = compute_content_hash(raw_content)

        sections = []
        for s in data.get("sections", []):
            sections.append(
                SectionItem(
                    section_number=s.get("section_number", "General"),
                    title=s.get("title", ""),
                    text=normalize_text(s.get("text", "")),
                )
            )

        return RegulatoryDocument(
            document_id=data.get("document_id", file_path.stem.upper()),
            title=data.get("document_title", data.get("title", file_path.stem)),
            source_name=data.get("source_name", "Official Government Source"),
            source_url=data.get("source_url", "https://niveshmitra.up.nic.in"),
            authority=data.get("authority", "Statutory Regulatory Authority"),
            jurisdiction=data.get("jurisdiction", "Uttar Pradesh"),
            document_type=data.get("document_type", "Act"),
            file_path=str(file_path),
            retrieved_at=data.get("retrieved_at", "2026-09-04T00:00:00Z"),
            last_verified_at=data.get("last_verified_at", "2026-09-04T00:00:00Z"),
            is_official=bool(data.get("is_official", False)),
            content_hash=content_hash,
            disclaimer=data.get("disclaimer", "DEMO / SYNTHETIC — NOT OFFICIAL REGULATORY TEXT"),
            raw_text=raw_content,
            sections=sections,
        )

    def _parse_markdown_document(self, file_path: Path) -> Optional[RegulatoryDocument]:
        """Parses a Markdown regulation document with optional YAML-like frontmatter."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        content_hash = compute_content_hash(content)
        metadata: Dict[str, str] = {}
        body = content

        # Check for simple frontmatter (between --- delimiters)
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm_lines = parts[1].strip().split("\n")
                for line in fm_lines:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        metadata[k.strip().lower()] = v.strip()
                body = parts[2].strip()

        # Parse markdown headings as sections
        sections: List[SectionItem] = []
        heading_matches = list(re.finditer(r"^(#{1,3})\s+(.+)$", body, re.MULTILINE))

        if heading_matches:
            for i, match in enumerate(heading_matches):
                heading_title = match.group(2).strip()
                start_pos = match.end()
                end_pos = heading_matches[i + 1].start() if i + 1 < len(heading_matches) else len(body)
                section_body = body[start_pos:end_pos].strip()

                sec_num = heading_title
                sec_title = ""
                if ":" in heading_title:
                    sec_num, sec_title = heading_title.split(":", 1)

                sections.append(
                    SectionItem(
                        section_number=sec_num.strip(),
                        title=sec_title.strip() or sec_num.strip(),
                        text=normalize_text(section_body),
                    )
                )
        else:
            sections.append(
                SectionItem(
                    section_number="General",
                    title="Regulatory Text",
                    text=normalize_text(body),
                )
            )

        doc_id = metadata.get("document_id", file_path.stem.upper())
        title = metadata.get("title", file_path.stem.replace("_", " ").title())

        return RegulatoryDocument(
            document_id=doc_id,
            title=title,
            source_name=metadata.get("source_name", "UPPCB / Nivesh Mitra Single Window Portal"),
            source_url=metadata.get("source_url", "https://niveshmitra.up.nic.in"),
            authority=metadata.get("authority", "Uttar Pradesh Pollution Control Board (UPPCB)"),
            jurisdiction=metadata.get("jurisdiction", "Uttar Pradesh"),
            document_type=metadata.get("document_type", "Act"),
            file_path=str(file_path),
            retrieved_at=metadata.get("retrieved_at", "2026-09-04T00:00:00Z"),
            last_verified_at=metadata.get("last_verified_at", "2026-09-04T00:00:00Z"),
            is_official=metadata.get("is_official", "false").lower() == "true",
            content_hash=content_hash,
            disclaimer=metadata.get("disclaimer", "DEMO / SYNTHETIC — NOT OFFICIAL REGULATORY TEXT"),
            raw_text=body,
            sections=sections,
        )

    def _parse_text_document(self, file_path: Path) -> Optional[RegulatoryDocument]:
        """Parses a plain text regulation document with key-value headers."""
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        metadata: Dict[str, str] = {}
        body_lines = []
        in_header = True

        for line in lines:
            line_str = line.strip()
            if in_header and ":" in line_str and not line_str.startswith("Section"):
                k, v = line_str.split(":", 1)
                metadata[k.strip().lower()] = v.strip()
            else:
                in_header = False
                body_lines.append(line)

        body = "\n".join(body_lines).strip()
        content_hash = compute_content_hash(body)

        # Parse sections separated by "Section X:"
        sections: List[SectionItem] = []
        sec_splits = re.split(r"(Section\s+\d+[^:\n]*:)", body)

        if len(sec_splits) > 1:
            for i in range(1, len(sec_splits), 2):
                header = sec_splits[i].strip().rstrip(":")
                text = sec_splits[i + 1].strip() if i + 1 < len(sec_splits) else ""
                sections.append(
                    SectionItem(
                        section_number=header,
                        title=header,
                        text=normalize_text(text),
                    )
                )
        else:
            sections.append(
                SectionItem(
                    section_number="General",
                    title="Statutory Text",
                    text=normalize_text(body),
                )
            )

        doc_id = metadata.get("document_id", file_path.stem.upper())
        title = metadata.get("title", file_path.stem.replace("_", " ").title())

        return RegulatoryDocument(
            document_id=doc_id,
            title=title,
            source_name=metadata.get("source_name", "Official Single Window Portal"),
            source_url=metadata.get("source_url", "https://niveshmitra.up.nic.in"),
            authority=metadata.get("authority", "Regulatory Authority"),
            jurisdiction=metadata.get("jurisdiction", "Uttar Pradesh"),
            document_type=metadata.get("document_type", "Regulation"),
            file_path=str(file_path),
            retrieved_at=metadata.get("retrieved_at", "2026-09-04T00:00:00Z"),
            last_verified_at=metadata.get("last_verified_at", "2026-09-04T00:00:00Z"),
            is_official=metadata.get("is_official", "false").lower() == "true",
            content_hash=content_hash,
            disclaimer=metadata.get("disclaimer", "DEMO / SYNTHETIC — NOT OFFICIAL REGULATORY TEXT"),
            raw_text=body,
            sections=sections,
        )

    def load_regulations(self) -> List[RegulatoryDocument]:
        """Discovers and parses local regulations (.json, .md, .txt) with duplicate detection."""
        documents: List[RegulatoryDocument] = []
        if not self.regulations_dir.exists():
            return documents

        for file_path in sorted(self.regulations_dir.iterdir()):
            if file_path.name.startswith(".") or file_path.name == "README.md":
                continue

            doc: Optional[RegulatoryDocument] = None
            if file_path.suffix.lower() == ".json":
                doc = self._parse_json_document(file_path)
            elif file_path.suffix.lower() == ".md":
                doc = self._parse_markdown_document(file_path)
            elif file_path.suffix.lower() == ".txt":
                doc = self._parse_text_document(file_path)

            if doc:
                # Deduplication check
                if doc.content_hash in self._seen_hashes or doc.document_id in self._seen_doc_ids:
                    # Duplicate detected
                    continue
                self._seen_hashes.add(doc.content_hash)
                self._seen_doc_ids.add(doc.document_id)
                documents.append(doc)

        return documents

    def load_approvals_as_documents(self) -> List[RegulatoryDocument]:
        """Converts approvals.csv entries into standardized RegulatoryDocuments."""
        documents: List[RegulatoryDocument] = []
        if not self.csv_path.exists():
            return documents

        with open(self.csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                aid = row.get("approval_id", "").strip()
                if not aid or aid in self._seen_doc_ids:
                    continue

                full_str = f"{aid}_{row.get('approval_name', '')}_{row.get('description', '')}"
                chash = compute_content_hash(full_str)
                if chash in self._seen_hashes:
                    continue

                sections = [
                    SectionItem(
                        section_number="Statutory Scope",
                        title=row.get("approval_name", "").strip(),
                        text=normalize_text(row.get("description", "").strip()),
                    ),
                    SectionItem(
                        section_number="Governing Act & Rules",
                        title="Statutory Legal Reference",
                        text=normalize_text(row.get("act_rules", "").strip()),
                    ),
                    SectionItem(
                        section_number="Eligibility Criteria",
                        title="Who Can Apply",
                        text=normalize_text(row.get("who_can_apply", "").strip()),
                    ),
                    SectionItem(
                        section_number="Conditions & Prerequisites",
                        title="Mandatory Operating Conditions",
                        text=normalize_text(row.get("conditions", "").strip() or "Standard statutory compliance required."),
                    ),
                ]

                doc = RegulatoryDocument(
                    document_id=f"APP_{aid}",
                    title=f"{row.get('approval_name', '').strip()} ({aid})",
                    source_name=row.get("source_name", "").strip() or "Official Single Window Portal",
                    source_url=row.get("source_url", "").strip() or "https://niveshmitra.up.nic.in",
                    authority=row.get("authority", "").strip(),
                    jurisdiction=row.get("state", "").strip(),
                    document_type="Catalog",
                    file_path=str(self.csv_path),
                    retrieved_at=row.get("retrieved_at", "").strip() or "2026-09-04T00:00:00Z",
                    last_verified_at=row.get("last_verified_at", "").strip() or "2026-09-04T00:00:00Z",
                    is_official=False,
                    content_hash=chash,
                    disclaimer="DEMO / SYNTHETIC — NOT OFFICIAL REGULATORY TEXT",
                    raw_text=full_str,
                    sections=sections,
                )
                self._seen_hashes.add(chash)
                self._seen_doc_ids.add(doc.document_id)
                documents.append(doc)

        return documents

    def ingest_all(self) -> List[RegulatoryDocument]:
        """Ingests all valid unique documents from regulations directory and CSV catalog."""
        return self.load_regulations() + self.load_approvals_as_documents()
