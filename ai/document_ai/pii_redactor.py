"""
PII Redaction and Data Privacy Protection

Sanitizes extracted document text by detecting and masking sensitive Personal Identifiable
Information (PII) including Aadhaar, PAN, Bank Accounts, Passwords, and Auth Tokens.
"""

import re
from typing import Tuple

# Regex patterns for sensitive identifiers
AADHAAR_PATTERN = re.compile(r"\b(\d{4})[-\s](\d{4})[-\s](\d{4})\b")
PAN_PATTERN = re.compile(r"\b([A-Z]{5})([0-9]{4})([A-Z])\b")
BANK_ACC_PATTERN = re.compile(r"\b(?:A/C|Account|Acc|Bank\s*Acc(?:ount)?(?:\s*No\.?)?|Bank\s*No\.?)[\s:]*(\d{9,18})\b", re.IGNORECASE)
PASSWORD_TOKEN_PATTERN = re.compile(r"\b(?:password|token|secret|key)[\s:=]+([^\s,;]+)", re.IGNORECASE)


def redact_pii(text: str) -> Tuple[str, bool]:
    """
    Masks sensitive personal and financial information from extracted text.
    Returns (redacted_text, pii_detected_flag).
    """
    if not text:
        return "", False

    pii_detected = False
    redacted = text

    # 1. Mask Bank Account numbers first
    if BANK_ACC_PATTERN.search(redacted):
        pii_detected = True
        redacted = BANK_ACC_PATTERN.sub(r"Bank Acc: [REDACTED_BANK_AC]", redacted)

    # 2. Mask Aadhaar: e.g. 1234 5678 9012 or 1234-5678-9012 -> XXXX-XXXX-9012
    if AADHAAR_PATTERN.search(redacted):
        pii_detected = True
        redacted = AADHAAR_PATTERN.sub(r"XXXX-XXXX-\3", redacted)

    # 3. Mask PAN: e.g. ABCDE1234F -> XXXXX1234F
    if PAN_PATTERN.search(redacted):
        pii_detected = True
        redacted = PAN_PATTERN.sub(r"XXXXX\2\3", redacted)

    # 4. Mask Passwords / Auth Tokens
    if PASSWORD_TOKEN_PATTERN.search(redacted):
        pii_detected = True
        redacted = PASSWORD_TOKEN_PATTERN.sub(r"password: [REDACTED_SECRET]", redacted)

    return redacted, pii_detected
