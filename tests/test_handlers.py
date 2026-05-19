"""Tests for the s3-monitor Lambda handler."""

from __future__ import annotations

import datetime
import importlib
import sys
from pathlib import Path

import boto3
import pytest
from moto import mock_aws

REGION = "eu-west-1"
BUCKET = "test-monitoring-bucket"
PREFIX = "backups/"
SENDER = "sender@example.com"
RECIPIENTS = "recipient1@example.com recipient2@example.com"


def _put(s3, key: str, *, days_old: int) -> None:
    """Upload an object then backdate its LastModified by ``days_old`` days.

    moto stores LastModified as the upload time, so we override via copy-in-place
    with a metadata change is not enough; instead we patch the object's mtime
    directly through moto's internal backend.
    """
    s3.put_object(Bucket=BUCKET, Key=key, Body=b"x")
    if days_old == 0:
        return
    from moto.s3.models import s3_backends

    backend = s3_backends["123456789012"]["global"]
    obj = backend.buckets[BUCKET].keys[key]
    new_dt = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=days_old)
    obj.last_modified = new_dt


def _import_handlers():
    repo_root = Path(__file__).resolve().parent.parent
    python_dir = repo_root / "python"
    if str(python_dir) not in sys.path:
        sys.path.insert(0, str(python_dir))
    if "handlers" in sys.modules:
        return importlib.reload(sys.modules["handlers"])
    return importlib.import_module("handlers")


@pytest.fixture
def lambda_env(monkeypatch):
    monkeypatch.setenv("MONITORINGBUCKET", BUCKET)
    monkeypatch.setenv("S3PREFIX", PREFIX)
    monkeypatch.setenv("SENDER", SENDER)
    monkeypatch.setenv("RECIPIENTS", RECIPIENTS)


@pytest.fixture
def aws(lambda_env):
    with mock_aws():
        s3 = boto3.client("s3", region_name=REGION)
        s3.create_bucket(
            Bucket=BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION},
        )
        ses = boto3.client("ses", region_name=REGION)
        ses.verify_email_identity(EmailAddress=SENDER)
        handlers = _import_handlers()
        yield {"s3": s3, "ses": ses, "handlers": handlers}


def _sent_count(ses) -> int:
    return ses.get_send_statistics()["SendDataPoints"] and sum(
        p.get("DeliveryAttempts", 0) for p in ses.get_send_statistics()["SendDataPoints"]
    )


def test_backup_today_present_no_email(aws):
    s3 = aws["s3"]
    handlers = aws["handlers"]
    _put(s3, f"{PREFIX}today.tar.gz", days_old=0)

    handlers.main(None, None)

    assert _sent_count(aws["ses"]) == 0


def test_backup_stale_sends_email_with_latest(aws):
    s3 = aws["s3"]
    handlers = aws["handlers"]
    _put(s3, f"{PREFIX}old.tar.gz", days_old=10)
    _put(s3, f"{PREFIX}newer-but-stale.tar.gz", days_old=2)

    handlers.main(None, None)

    assert _sent_count(aws["ses"]) >= 1


def test_no_objects_sends_no_backups_email(aws):
    handlers = aws["handlers"]

    handlers.main(None, None)

    assert _sent_count(aws["ses"]) >= 1


def test_lexicographic_order_does_not_fool_latest_detection(aws, monkeypatch):
    """A key sorted last alphabetically should NOT be treated as latest."""
    s3 = aws["s3"]
    handlers = aws["handlers"]
    _put(s3, f"{PREFIX}zzz-old.tar.gz", days_old=15)
    _put(s3, f"{PREFIX}aaa-recent.tar.gz", days_old=3)

    captured = {}

    def fake_notify(config, *, subject, file_date, file_name, file_size):
        captured["subject"] = subject
        captured["file_name"] = file_name
        captured["file_date"] = file_date

    monkeypatch.setattr(handlers, "_notify", fake_notify)
    handlers.main(None, None)

    assert captured["file_name"] == f"{PREFIX}aaa-recent.tar.gz"
    assert "Backup stale" in captured["subject"]


def test_empty_recipients_raises(monkeypatch, aws):
    handlers = aws["handlers"]
    monkeypatch.setenv("RECIPIENTS", "   ")

    with pytest.raises(RuntimeError, match="RECIPIENTS"):
        handlers.main(None, None)


def test_missing_bucket_raises(monkeypatch, aws):
    handlers = aws["handlers"]
    monkeypatch.delenv("MONITORINGBUCKET")

    with pytest.raises(RuntimeError, match="MONITORINGBUCKET"):
        handlers.main(None, None)


def test_missing_sender_raises(monkeypatch, aws):
    handlers = aws["handlers"]
    monkeypatch.delenv("SENDER")

    with pytest.raises(RuntimeError, match="SENDER"):
        handlers.main(None, None)


def test_sizeof_fmt():
    handlers = _import_handlers()

    assert handlers.sizeof_fmt(0) == "0.0B"
    assert handlers.sizeof_fmt(1024) == "1.0KiB"
    assert handlers.sizeof_fmt(1024 * 1024) == "1.0MiB"
