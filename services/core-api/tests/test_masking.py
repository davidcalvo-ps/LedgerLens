import logging

import pytest
from django.core.management import call_command

from modules.accounts.masking import MaskEmailsFilter, mask_email, mask_emails_in
from modules.accounts.models import Membership


@pytest.mark.parametrize(
    ("email", "masked"),
    [
        ("lucia@lumen.example", "l***@lumen.example"),
        ("a@b.example", "a***@b.example"),
        ("not-an-email", "***"),
        ("@lumen.example", "***"),
        ("", "***"),
    ],
)
def test_mask_email(email, masked) -> None:
    assert mask_email(email) == masked


def test_mask_emails_in_free_text() -> None:
    text = "login failed for tomas@harbor.example, retry by martin@books.example"

    assert mask_emails_in(text) == (
        "login failed for t***@harbor.example, retry by m***@books.example"
    )


def make_record(msg: str, *args) -> logging.LogRecord:
    return logging.LogRecord("test", logging.INFO, __file__, 1, msg, args, None)


def test_log_filter_masks_formatted_arguments() -> None:
    record = make_record("signed in: %s (%s)", "sara@lumen.example", "analyst")

    assert MaskEmailsFilter().filter(record) is True
    assert record.getMessage() == "signed in: s***@lumen.example (analyst)"


def test_log_filter_leaves_plain_messages_alone() -> None:
    record = make_record("health check ok")

    MaskEmailsFilter().filter(record)

    assert record.msg == "health check ok"


def test_django_logging_masks_emails(caplog) -> None:
    logger = logging.getLogger("modules.accounts")
    # The console handler configured in settings.LOGGING carries the filter.
    assert any(
        isinstance(f, MaskEmailsFilter)
        for handler in logging.getLogger().handlers
        for f in handler.filters
    )

    caplog.handler.addFilter(MaskEmailsFilter())
    with caplog.at_level(logging.INFO, logger="modules.accounts"):
        logger.info("password reset for %s", "lucia@lumen.example")

    assert "lucia@lumen.example" not in caplog.text
    assert "l***@lumen.example" in caplog.text


@pytest.mark.django_db
def test_membership_str_masks_email(people) -> None:
    membership = Membership.objects.get(user=people["owner"])

    assert str(membership) == "o***@a.example @ Org A (owner)"


@pytest.mark.django_db
def test_seed_output_masks_demo_emails(settings, capsys) -> None:
    settings.DEBUG = True

    call_command("seed_demo_orgs", password="seed-test-password-123")

    out = capsys.readouterr().out
    assert "lucia@lumen.example" not in out
    assert "l***@lumen.example: owner @ lumen-studio" in out
