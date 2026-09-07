"""
Document Expiry and Validity Period Checker

Evaluates certificate issue and expiry dates against current calendar dates,
flagging expired or expiring certificates without making legal renewal conclusions.
"""

import re
from datetime import datetime, date, timezone
from typing import Optional, Tuple
from ai.document_ai.models import ExpiryStatus


def parse_date(date_str: str) -> Optional[date]:
    """Attempts to parse common date formats (YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY, DD Month YYYY)."""
    if not date_str or not date_str.strip():
        return None

    cleaned = date_str.strip()
    date_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y/%m/%d",
        "%d %B %Y",
        "%d %b %Y",
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue

    return None


def check_expiry(
    issue_date_str: Optional[str],
    expiry_date_str: Optional[str],
    current_date: Optional[date] = None,
    threshold_days: int = 30,
) -> Tuple[ExpiryStatus, Optional[int], str]:
    """
    Checks document expiry status against a reference date.
    Returns (ExpiryStatus, days_until_expiry, explanation).
    """
    ref_date = current_date or datetime.now(timezone.utc).date()

    if not expiry_date_str or not expiry_date_str.strip():
        return (
            ExpiryStatus.NO_EXPIRY_INFORMATION,
            None,
            "No expiry date detected in document; requires manual verification.",
        )

    exp_lower = expiry_date_str.strip().lower()
    if exp_lower in ("permanent", "lifetime", "perpetual", "na", "n/a", "not applicable"):
        return (
            ExpiryStatus.VALID,
            9999,
            f"Document granted with permanent / lifetime validity ('{expiry_date_str}').",
        )

    parsed_exp = parse_date(expiry_date_str)
    if not parsed_exp:
        return (
            ExpiryStatus.NO_EXPIRY_INFORMATION,
            None,
            f"Could not parse expiry date string '{expiry_date_str}'.",
        )

    delta_days = (parsed_exp - ref_date).days

    if delta_days < 0:
        return (
            ExpiryStatus.EXPIRED,
            delta_days,
            f"Document expired {abs(delta_days)} days ago (Expiry date: {parsed_exp.isoformat()}).",
        )
    elif delta_days <= threshold_days:
        return (
            ExpiryStatus.EXPIRING_SOON,
            delta_days,
            f"Document expires in {delta_days} days (Expiry date: {parsed_exp.isoformat()}) - renewal recommended.",
        )
    else:
        return (
            ExpiryStatus.VALID,
            delta_days,
            f"Document is valid for {delta_days} more days (Expiry date: {parsed_exp.isoformat()}).",
        )
