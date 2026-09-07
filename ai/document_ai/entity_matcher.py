"""
Enterprise Entity Name Matching and Normalization

Performs fuzzy and token-based entity name cross-checking with corporate suffix canonicalization
(e.g., 'Private Limited' vs 'Pvt Ltd') without incorrectly merging distinct companies.
"""

import re
from typing import Tuple
from ai.document_ai.models import EntityMatchStatus

# Mapping of corporate legal entity suffixes to canonical forms
CORPORATE_SUFFIX_MAP = {
    r"\bprivate\s+limited\b": "pvt ltd",
    r"\bpvt\.?\s*ltd\.?\b": "pvt ltd",
    r"\bp\.?\s*ltd\.?\b": "pvt ltd",
    r"\blimited\b": "ltd",
    r"\bltd\.?\b": "ltd",
    r"\blimited\s+liability\s+partnership\b": "llp",
    r"\bllp\.?\b": "llp",
    r"\bincorporated\b": "inc",
    r"\binc\.?\b": "inc",
    r"\bcorporation\b": "corp",
    r"\bcorp\.?\b": "corp",
    r"\bcompany\b": "co",
    r"\bco\.?\b": "co",
    r"\bproprietorship\b": "prop",
    r"\benterprises?\b": "ent",
}


def normalize_entity_name(name: str) -> str:
    """Normalizes punctuation, whitespace, and corporate suffixes for consistent matching."""
    if not name:
        return ""

    text = name.strip().lower()
    # Replace corporate suffixes with canonical tokens
    for pattern, canonical in CORPORATE_SUFFIX_MAP.items():
        text = re.sub(pattern, canonical, text)

    # Remove non-alphanumeric characters except spaces
    text = re.sub(r"[^\w\s]", " ", text)
    # Collapse multiple whitespaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def match_entity_names(expected: str, extracted: str) -> Tuple[EntityMatchStatus, str]:
    """
    Compares the expected entity name from the business profile with extracted document text.
    Returns (EntityMatchStatus, explanation).
    """
    if not expected or not expected.strip():
        return EntityMatchStatus.UNKNOWN, "Expected enterprise name is missing or unspecified."

    if not extracted or not extracted.strip():
        return EntityMatchStatus.UNKNOWN, "No enterprise entity name could be extracted from the document."

    norm_expected = normalize_entity_name(expected)
    norm_extracted = normalize_entity_name(extracted)

    # 1. Exact Match after basic normalization
    if norm_expected == norm_extracted:
        return EntityMatchStatus.EXACT_MATCH, "Enterprise name exactly matches business profile."

    # 2. Token Overlap & Suffix Variations
    exp_tokens = set(norm_expected.split())
    ext_tokens = set(norm_extracted.split())

    # Filter out pure suffix tokens for core name comparison
    suffix_tokens = {"pvt", "ltd", "llp", "inc", "corp", "co", "prop", "ent"}
    core_exp = exp_tokens - suffix_tokens
    core_ext = ext_tokens - suffix_tokens

    if core_exp and core_exp == core_ext:
        return EntityMatchStatus.LIKELY_MATCH, "Corporate legal suffix variation detected; core enterprise name matches."

    if core_exp and core_exp.issubset(core_ext):
        return EntityMatchStatus.LIKELY_MATCH, "Extracted name contains full expected enterprise name along with branch/unit identifier."

    if core_exp and core_ext and len(core_exp & core_ext) / max(len(core_exp), len(core_ext)) >= 0.67:
        return EntityMatchStatus.LIKELY_MATCH, f"High token overlap between expected '{expected}' and extracted '{extracted}'."

    return EntityMatchStatus.NO_MATCH, f"Entity name mismatch: Expected '{expected}', but document contains '{extracted}'."
