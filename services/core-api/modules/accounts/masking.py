"""Masking for personal data that ends up outside the API response.

Log lines, model `__str__` values and management-command output are read by
people who do not need to know who a member is, and they are copied into
support tickets and CI logs. Anything written there goes through these
helpers so an email address is recognisable to its owner but not harvestable:

    mask_email("lucia@lumen.example")  ->  "l***@lumen.example"
"""

import logging
import re

EMAIL_PATTERN = re.compile(r"(?P<local>[A-Za-z0-9._%+-]+)@(?P<domain>[A-Za-z0-9.-]+\.[A-Za-z]{2,})")
MASK = "***"


def mask_email(email: str) -> str:
    """Keep the first character and the domain; hide the rest of the local part."""
    local, sep, domain = (email or "").partition("@")
    if not sep or not local or not domain:
        return MASK
    return f"{local[0]}{MASK}@{domain}"


def mask_emails_in(text: str) -> str:
    """Mask every email address found in free text."""
    return EMAIL_PATTERN.sub(lambda match: mask_email(match.group(0)), text)


class MaskEmailsFilter(logging.Filter):
    """Logging filter that masks email addresses in the rendered message.

    The record is rewritten in place (message formatted, args cleared) so every
    handler after this filter sees the masked text.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except (TypeError, ValueError):
            return True  # leave malformed records for the formatter to report
        masked = mask_emails_in(message)
        if masked != message or record.args:
            record.msg = masked
            record.args = None
        return True
