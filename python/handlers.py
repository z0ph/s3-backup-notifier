import datetime
import boto3
import os
import logging
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
bucket_name = os.environ.get("MONITORINGBUCKET")
s3_prefix = os.environ.get("S3PREFIX")
recipients = os.environ.get("RECIPIENTS")
subject = "S3 Backup Notifier - Backup Failed ❌"
sender = f"S3 Backup Notifier <{os.environ.get('SENDER')}>"
aws_region = os.environ.get("AWSREGION")

# Get Today's date
today = datetime.date.today()

# AWS Connection
session = boto3.Session(region_name=aws_region)
s3 = session.resource("s3")
ses = session.client("ses")

# Access the S3 bucket
bucket = s3.Bucket(bucket_name)
objs = bucket.objects.filter(Prefix=s3_prefix).all()


# Convert to Human Readable
def sizeof_fmt(num, suffix="B"):
    """Convert a file size to a human-readable format."""
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def main(event, context):
    """Main function to check for today's backup and send notifications if missing."""
    try:
        backup_success = False
        for obj in objs:
            file_date = obj.last_modified.date()
            file_name = obj.key
            file_size = sizeof_fmt(obj.size)
            logger.info(f"Checking file: {file_date} {file_name} {file_size}")

            if file_date == today:
                logger.info("Backup OK, All Good")
                logger.info(f"--> {file_date} {file_name} {file_size}")
                backup_success = True
                break  # Exit loop if today's backup is found

        if not backup_success:
            logger.warning("No backup detected from today")
            notification(file_date=file_date, file_name=file_name, file_size=file_size)

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(f"ClientError: {e.response['Error']['Message']}")
        if error_code == "404":
            logger.error("There is no file in this bucket")
        else:
            logger.exception("An unexpected error occurred")


def notification(file_date, file_name, file_size):
    """Send a notification email about the last backup."""
    try:
        CHARSET = "UTF-8"
        BODY_TEXT = (
            "S3 Backup Notifier\r\n"
            "Last backup comes from:\r\n"
            f"{file_date}, {file_name}, {file_size}\r\n"
            "S3 Backup Notifier"
        )
        BODY_HTML = f"""
            <html>
                <body>
                    <h1>S3 Backup Notifier 👨‍🚒</h1>
                    <h3>Last backup comes from:</h3>
                    <table cellpadding="4" cellspacing="4" border="1">
                    <tr><td>Date</td><td>Name</td><td>Size</td></tr>
                    <tr><td>{file_date}</td><td>{file_name}</td><td>{file_size}</td></tr>
                    </table>
                    <p><a href="https://github.com/z0ph/s3-backup-notifier">S3 Backup Notifier</a></p>
                </body>
            </html>
            """

        # Send the email
        response = ses.send_email(
            Destination={"ToAddresses": recipients.split()},
            Message={
                "Body": {
                    "Html": {"Charset": CHARSET, "Data": BODY_HTML},
                    "Text": {"Charset": CHARSET, "Data": BODY_TEXT},
                },
                "Subject": {"Charset": CHARSET, "Data": subject},
            },
            Source=sender,
        )
        logger.info(f"Email sent! Message ID: {response['MessageId']}")

    except ClientError as e:
        logger.error(f"Failed to send email: {e.response['Error']['Message']}")


# Run locally for testing purpose
if __name__ == "__main__":
    main(0, 0)
