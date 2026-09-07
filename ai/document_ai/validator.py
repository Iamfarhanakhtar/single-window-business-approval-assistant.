"""
Document Pre-Validation and Completeness Engine

Executes deterministic rule-based pre-validation checks across readability,
entity names, validity periods, and required document checklists.
"""

import re
from typing import List, Tuple, Optional, Set
from ai.document_ai.models import (
    DocumentInput,
    ExtractedDocument,
    DocumentValidationResult,
    DocumentStatus,
    EntityMatchStatus,
    ExpiryStatus,
    DocumentTypeMatch,
    CheckItem,
    CompletenessReport,
)
from ai.document_ai.extractor import DocumentExtractor
from ai.document_ai.entity_matcher import match_entity_names
from ai.document_ai.expiry_checker import check_expiry


def check_document_type_match(expected: Optional[str], uploaded: str, text: str) -> Tuple[DocumentTypeMatch, str]:
    """
    Compares expected document type against uploaded type and document text.
    """
    if not expected or not expected.strip():
        return DocumentTypeMatch.UNKNOWN, "No expected document type specified."

    norm_exp = re.sub(r"[^\w\s]", " ", expected.lower()).strip()
    norm_upl = re.sub(r"[^\w\s]", " ", uploaded.lower()).strip()
    norm_txt = re.sub(r"[^\w\s]", " ", text.lower()).strip()

    if norm_exp == norm_upl:
        return DocumentTypeMatch.MATCH, "Document category exactly matches requirement."

    exp_tokens = set(norm_exp.split())
    upl_tokens = set(norm_upl.split())

    # Stop words
    stop_words = {"and", "or", "the", "of", "in", "for", "a", "an", "copy", "certificate", "plan"}
    sig_exp = exp_tokens - stop_words
    sig_upl = upl_tokens - stop_words

    if sig_exp and sig_exp.issubset(sig_upl):
        return DocumentTypeMatch.LIKELY_MATCH, f"Uploaded document category '{uploaded}' aligns with expected '{expected}'."

    # Check if expected keywords appear prominently in document text
    if sig_exp and len(sig_exp & set(norm_txt.split())) / len(sig_exp) >= 0.75:
        return DocumentTypeMatch.LIKELY_MATCH, f"Document content contains key statutory terms matching '{expected}'."

    if sig_exp and sig_upl and len(sig_exp & sig_upl) == 0:
        return DocumentTypeMatch.MISMATCH, f"Document type mismatch: Expected '{expected}', but uploaded as '{uploaded}'."

    return DocumentTypeMatch.LIKELY_MATCH, f"Partial category alignment between '{uploaded}' and expected '{expected}'."


class DocumentValidator:
    """
    Validates uploaded enterprise documents against application metadata and checklists.
    """

    def __init__(self, extractor: Optional[DocumentExtractor] = None):
        self.extractor = extractor or DocumentExtractor()

    def validate_document(
        self,
        doc_input: DocumentInput,
        extracted: Optional[ExtractedDocument] = None,
    ) -> DocumentValidationResult:
        """
        Executes pre-validation checks on an uploaded document.
        """
        if extracted is None:
            extracted = self.extractor.extract(
                document_id=doc_input.document_id,
                file_path=doc_input.file_path,
                document_type=doc_input.document_type,
            )

        checks: List[CheckItem] = []
        warnings: List[str] = []
        errors: List[str] = []

        # 1. Readability Check
        if not extracted.is_readable:
            errors.append(f"Document cannot be read or parsed: {extracted.extracted_text}")
            checks.append(CheckItem(check_name="Readability", passed=False, details=extracted.extracted_text))
            return DocumentValidationResult(
                document_id=doc_input.document_id,
                filename=doc_input.filename,
                status=DocumentStatus.UNREADABLE,
                entity_match=EntityMatchStatus.UNKNOWN,
                expiry_status=ExpiryStatus.NO_EXPIRY_INFORMATION,
                type_match=DocumentTypeMatch.UNKNOWN,
                checks=checks,
                warnings=warnings,
                errors=errors,
                confidence=0.0,
                requires_human_verification=True,
            )

        checks.append(CheckItem(check_name="Readability", passed=True, details="Document text successfully parsed."))

        # 2. Document Type Match Check
        type_match, type_expl = check_document_type_match(
            expected=doc_input.expected_document_type,
            uploaded=doc_input.document_type,
            text=extracted.extracted_text,
        )
        if type_match == DocumentTypeMatch.MISMATCH:
            errors.append(type_expl)
            checks.append(CheckItem(check_name="Document Type Match", passed=False, details=type_expl))
        elif type_match == DocumentTypeMatch.LIKELY_MATCH:
            warnings.append(type_expl)
            checks.append(CheckItem(check_name="Document Type Match", passed=True, details=type_expl))
        else:
            checks.append(CheckItem(check_name="Document Type Match", passed=True, details=type_expl))

        # 3. Entity Name Match Check
        entity_match, ent_expl = match_entity_names(
            expected=doc_input.expected_entity_name or "",
            extracted=extracted.entity_name or "",
        )
        if entity_match == EntityMatchStatus.NO_MATCH:
            errors.append(ent_expl)
            checks.append(CheckItem(check_name="Entity Name Consistency", passed=False, details=ent_expl))
        elif entity_match == EntityMatchStatus.LIKELY_MATCH:
            warnings.append(ent_expl)
            checks.append(CheckItem(check_name="Entity Name Consistency", passed=True, details=ent_expl))
        elif entity_match == EntityMatchStatus.UNKNOWN:
            warnings.append(ent_expl)
            checks.append(CheckItem(check_name="Entity Name Consistency", passed=True, details=ent_expl))
        else:
            checks.append(CheckItem(check_name="Entity Name Consistency", passed=True, details=ent_expl))

        # 4. Expiry / Validity Period Check
        expiry_status, days_left, exp_expl = check_expiry(
            issue_date_str=extracted.issue_date,
            expiry_date_str=extracted.expiry_date,
        )
        if expiry_status == ExpiryStatus.EXPIRED:
            errors.append(exp_expl)
            checks.append(CheckItem(check_name="Validity Period", passed=False, details=exp_expl))
        elif expiry_status == ExpiryStatus.EXPIRING_SOON:
            warnings.append(exp_expl)
            checks.append(CheckItem(check_name="Validity Period", passed=True, details=exp_expl))
        elif expiry_status == ExpiryStatus.NO_EXPIRY_INFORMATION:
            warnings.append(exp_expl)
            checks.append(CheckItem(check_name="Validity Period", passed=True, details=exp_expl))
        else:
            checks.append(CheckItem(check_name="Validity Period", passed=True, details=exp_expl))

        # 5. Document Identification Number Check
        if not extracted.document_number:
            warnings.append("No explicit registration / license identification number detected.")
            checks.append(CheckItem(check_name="Certificate Number", passed=False, details="No document number detected."))
        else:
            checks.append(CheckItem(check_name="Certificate Number", passed=True, details=f"Document ID: {extracted.document_number}"))

        # Determine overall pre-validation status (data quality / pre-screening only)
        if errors:
            status = DocumentStatus.REQUIRES_HUMAN_VERIFICATION
        elif warnings:
            status = DocumentStatus.WARNING
        else:
            status = DocumentStatus.VALID

        # Composite validation confidence
        passed_checks = sum(1 for c in checks if c.passed)
        val_confidence = round(passed_checks / len(checks), 2) if checks else 0.0

        return DocumentValidationResult(
            document_id=doc_input.document_id,
            filename=doc_input.filename,
            status=status,
            entity_match=entity_match,
            expiry_status=expiry_status,
            type_match=type_match,
            checks=checks,
            warnings=warnings,
            errors=errors,
            confidence=val_confidence,
            days_until_expiry=days_left,
            requires_human_verification=True,
        )

    def check_completeness(
        self,
        required_documents: List[str],
        uploaded_documents: List[DocumentInput],
        application_id: Optional[str] = None,
    ) -> CompletenessReport:
        """
        Cross-checks the Rule Engine's required documents checklist against uploaded items.
        """
        uploaded_types = [doc.document_type.strip().lower() for doc in uploaded_documents]
        
        matched: List[str] = []
        missing: List[str] = []

        for req in required_documents:
            req_clean = req.strip()
            req_lower = req_clean.lower()
            
            # Match if exact or token overlap with any uploaded document type
            is_matched = False
            for upl in uploaded_types:
                if upl == req_lower or req_lower in upl or upl in req_lower:
                    is_matched = True
                    break
                # Token overlap check
                req_toks = set(req_lower.split())
                upl_toks = set(upl.split())
                if len(req_toks & upl_toks) >= 2:
                    is_matched = True
                    break

            if is_matched:
                matched.append(req_clean)
            else:
                missing.append(req_clean)

        total_req = len(required_documents)
        pct = round((len(matched) / total_req * 100.0), 1) if total_req > 0 else 100.0

        return CompletenessReport(
            application_id=application_id,
            required_documents=required_documents,
            uploaded_documents=[d.document_type for d in uploaded_documents],
            matched_documents=matched,
            missing_documents=missing,
            completeness_percentage=pct,
            is_complete=(len(missing) == 0),
        )
