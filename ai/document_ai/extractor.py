"""
Local Document Text and Entity Extractor

Extracts text from local files (.txt, .md, .csv, .json), performs conservative regex
extraction of key certificate fields, and enforces memory and privacy safeguards.
"""

import os
import json
import csv
import re
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from ai.document_ai.models import ExtractedDocument
from ai.document_ai.pii_redactor import redact_pii

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit to prevent OOM

# Extraction patterns - prioritized specific prefixes before general ones
DOC_NUM_PATTERN = re.compile(
    r"(?:Certificate\s*Number|Registration\s*Number|License\s*Number|Licence\s*Number|Drawing\s*Reference\s*No|Certificate\s*No|License\s*No|Licence\s*No|Registration\s*No|NOC\s*No|Consent\s*No|Ref\s*No|Ref\.?\s*No|No\.)[\s\.:#№\-]+([A-Z0-9\-\/]{4,35})",
    re.IGNORECASE,
)
ISSUE_DATE_PATTERN = re.compile(
    r"(?:Date\s*of\s*Issue|Issue\s*Date|Dated|Granted\s*On)[\s\.:]+(\d{4}-\d{2}-\d{2}|\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})",
    re.IGNORECASE,
)
EXPIRY_DATE_PATTERN = re.compile(
    r"(?:Valid\s*Up\s*To|Valid\s*Till|Valid\s*Through|Valid\s*to|Expiry\s*Date|Validity)[\s\.:]+(\d{4}-\d{2}-\d{2}|\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4}|Permanent|Lifetime|Perpetual)",
    re.IGNORECASE,
)
ENTITY_PATTERN = re.compile(
    r"(?:Applicant\s*Enterprise|Enterprise\s*Name|Company\s*Name|Unit\s*Name|Issued\s*To|Applicant|Occupier)[\*\s\.:]+([A-Za-z0-9\s\.\,\'\-]{3,60}(?:Pvt\s*Ltd|Private\s*Limited|Ltd|Limited|LLP|Inc|Corporation|Enterprises|Foods)?)",
    re.IGNORECASE,
)
AUTHORITY_PATTERN = re.compile(
    r"(?:Authority|Department|Board|Issued\s*By|Office\s*of)[\s\.:]+([A-Za-z0-9\s\.\,\(\)\-]{4,75})",
    re.IGNORECASE,
)


class DocumentExtractor:
    """
    Extracts text and key regulatory metadata from local files without external cloud APIs.
    """

    def read_file_content(self, file_path: str) -> Tuple[str, bool, str]:
        """
        Reads local file text within size limits.
        Returns (content_text, is_readable, error_message).
        """
        path = Path(file_path)
        if not path.exists():
            return "", False, f"File not found on disk: {file_path}"

        file_size = path.stat().st_size
        if file_size > MAX_FILE_SIZE_BYTES:
            return "", False, f"File exceeds maximum allowed size of 10MB ({file_size} bytes)."

        if file_size == 0:
            return "", False, "File is completely empty (0 bytes)."

        suffix = path.suffix.lower()

        try:
            if suffix in (".txt", ".md"):
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    return f.read(), True, ""

            elif suffix == ".csv":
                rows_text = []
                with open(path, mode="r", encoding="utf-8", errors="replace") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        rows_text.append(", ".join([cell.strip() for cell in row if cell.strip()]))
                return "\n".join(rows_text), True, ""

            elif suffix == ".json":
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # Convert dict to clean key: value text lines for uniform regex extraction
                        lines = [f"{k.replace('_', ' ').title()}: {v}" for k, v in data.items()]
                        return "\n".join(lines), True, ""
                    return json.dumps(data, indent=2), True, ""

            elif suffix == ".pdf":
                return "", False, "PDF_EXTRACTION_NOT_AVAILABLE: Local PDF extraction library is not configured."

            elif suffix in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
                return "", False, "OCR_NOT_AVAILABLE: Local OCR engine (e.g. Tesseract) is not installed."

            else:
                return "", False, f"Unsupported file extension '{suffix}'. Supported: .txt, .md, .csv, .json"

        except Exception as e:
            return "", False, f"Malformed file read error: {str(e)}"

    def extract_fields_from_text(self, text: str) -> Dict[str, Any]:
        """Performs pattern-based extraction for metadata fields."""
        fields: Dict[str, Any] = {
            "entity_name": None,
            "document_number": None,
            "issue_date": None,
            "expiry_date": None,
            "authority": None,
            "confidence": 0.0,
        }

        if not text:
            return fields

        detected_count = 0

        # Entity Name
        ent_match = ENTITY_PATTERN.search(text)
        if ent_match:
            fields["entity_name"] = ent_match.group(1).strip().rstrip(".,")
            detected_count += 1

        # Document Number
        doc_match = DOC_NUM_PATTERN.search(text)
        if doc_match:
            fields["document_number"] = doc_match.group(1).strip()
            detected_count += 1

        # Issue Date
        issue_match = ISSUE_DATE_PATTERN.search(text)
        if issue_match:
            fields["issue_date"] = issue_match.group(1).strip()
            detected_count += 1

        # Expiry Date
        exp_match = EXPIRY_DATE_PATTERN.search(text)
        if exp_match:
            fields["expiry_date"] = exp_match.group(1).strip()
            detected_count += 1

        # Authority
        auth_match = AUTHORITY_PATTERN.search(text)
        if auth_match:
            fields["authority"] = auth_match.group(1).strip().rstrip(".,")
            detected_count += 1

        # Confidence: ratio of detected fields
        fields["confidence"] = round(detected_count / 5.0, 2)
        return fields

    def extract(self, document_id: str, file_path: str, document_type: str) -> ExtractedDocument:
        """
        Loads document file, redacts PII, and extracts structured certificate fields.
        """
        filename = Path(file_path).name
        raw_text, is_readable, err_msg = self.read_file_content(file_path)

        if not is_readable:
            return ExtractedDocument(
                document_id=document_id,
                filename=filename,
                document_type=document_type,
                extracted_text=err_msg,
                redacted_text=err_msg,
                confidence=0.0,
                is_readable=False,
                pii_detected=False,
            )

        # Redact PII
        redacted_text, pii_detected = redact_pii(raw_text)
        fields = self.extract_fields_from_text(raw_text)

        return ExtractedDocument(
            document_id=document_id,
            filename=filename,
            document_type=document_type,
            extracted_text=raw_text,
            redacted_text=redacted_text,
            entity_name=fields["entity_name"],
            issue_date=fields["issue_date"],
            expiry_date=fields["expiry_date"],
            document_number=fields["document_number"],
            authority=fields["authority"],
            confidence=fields["confidence"],
            is_readable=True,
            pii_detected=pii_detected,
        )
