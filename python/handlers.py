"""S3 Backup Notifier Lambda handler.

Checks that an object with today's ``LastModified`` exists under a given
prefix in an S3 bucket and emits an SES email when it does not.
"""

import datetime
import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Lambda sets AWS_REGION for us, so reuse it instead of passing our own copy.
SESSION = boto3.Session(region_name=os.environ.get("AWS_REGION"))
S3 = SESSION.client("s3")
SES = SESSION.client("ses")

REPO_URL = "https://github.com/z0ph/s3-monitor"


def sizeof_fmt(num: float, suffix: str = "B") -> str:
    """Convert a byte count to a human-readable string."""
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def _load_config() -> dict:
    """Read env vars, validate, and normalize into a config dict."""
    bucket = os.environ.get("MONITORINGBUCKET")
    prefix = os.environ.get("S3PREFIX", "")
    sender = os.environ.get("SENDER")
    recipients_raw = os.environ.get("RECIPIENTS", "")

    if not bucket:
        raise RuntimeError("MONITORINGBUCKET env var is required")
    if not sender:
        raise RuntimeError("SENDER env var is required")

    recipients = recipients_raw.split()
    if not recipients:
        raise RuntimeError(
            "RECIPIENTS env var is required (whitespace-separated email list)"
        )

    return {
        "bucket": bucket,
        "prefix": prefix,
        "sender": sender,
        "recipients": recipients,
    }


def _find_latest_backup(bucket: str, prefix: str) -> dict | None:
    """Return the object with the most recent LastModified under prefix, or None."""
    paginator = S3.get_paginator("list_objects_v2")
    latest = None
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            if latest is None or obj["LastModified"] > latest["LastModified"]:
                latest = obj
    return latest


def main(event, context):
    """Check for today's backup and notify if missing."""
    config = _load_config()
    today = datetime.date.today()

    try:
        latest = _find_latest_backup(config["bucket"], config["prefix"])
    except ClientError as e:
        logger.exception(
            "Failed to list bucket s3://%s/%s: %s",
            config["bucket"],
            config["prefix"],
            e.response["Error"]["Message"],
        )
        raise

    if latest is None:
        logger.error("No backups found under s3://%s/%s", config["bucket"], config["prefix"])
        _notify(
            config,
            subject="S3 Backup Notifier - No backups found",
            file_date="No backups",
            file_name="No files",
            file_size="0B",
        )
        return

    file_date = latest["LastModified"].date()
    file_name = latest["Key"]
    file_size = sizeof_fmt(latest["Size"])

    if file_date == today:
        logger.info(
            "Backup OK - latest: %s %s %s", file_date, file_name, file_size
        )
        return

    logger.warning(
        "Latest backup is stale: %s %s %s (today=%s)",
        file_date,
        file_name,
        file_size,
        today,
    )
    _notify(
        config,
        subject=f"S3 Backup Notifier - Backup stale (last: {file_date})",
        file_date=file_date,
        file_name=file_name,
        file_size=file_size,
    )


def _notify(config: dict, *, subject: str, file_date, file_name: str, file_size: str) -> None:
    """Send an SES email describing the most recent backup we could find."""
    charset = "UTF-8"
    body_text = (
        "S3 Backup Notifier\r\n"
        "Last backup found:\r\n"
        f"{file_date}, {file_name}, {file_size}\r\n"
        f"{REPO_URL}"
    )
    body_html = f"""<html>
  <body style="font-family: -apple-system, Segoe UI, Roboto, sans-serif;">
    <h1>S3 Backup Notifier</h1>
    <h3>Last backup found:</h3>
    <table style="border-collapse: collapse;">
      <tr>
        <th style="border: 1px solid #ccc; padding: 6px;">Date</th>
        <th style="border: 1px solid #ccc; padding: 6px;">Name</th>
        <th style="border: 1px solid #ccc; padding: 6px;">Size</th>
      </tr>
      <tr>
        <td style="border: 1px solid #ccc; padding: 6px;">{file_date}</td>
        <td style="border: 1px solid #ccc; padding: 6px;">{file_name}</td>
        <td style="border: 1px solid #ccc; padding: 6px;">{file_size}</td>
      </tr>
    </table>
    <p><a href="{REPO_URL}">S3 Backup Notifier</a></p>
  </body>
</html>"""

    sender_addr = f"S3 Backup Notifier <{config['sender']}>"
    try:
        response = SES.send_email(
            Destination={"ToAddresses": config["recipients"]},
            Message={
                "Body": {
                    "Html": {"Charset": charset, "Data": body_html},
                    "Text": {"Charset": charset, "Data": body_text},
                },
                "Subject": {"Charset": charset, "Data": subject},
            },
            Source=sender_addr,
        )
        logger.info("Email sent - Message ID: %s", response["MessageId"])
    except ClientError as e:
        logger.error(
            "Failed to send email via SES: %s", e.response["Error"]["Message"]
        )
        raise


if __name__ == "__main__":
    main(None, None)
