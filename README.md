# S3 Monitor

S3 Monitor intend to check the last object (s3 key) with last_modified date in AWS S3, and if its older than today, send alerting email.

I'm using this to monitor my effective backup of Jeedom.

## Technical details

* Uses AWS Lambda function (Python)
* Scheduled (daily) with cron
* Uses AWS Simple Email Service (SES) for Emails Notifications

## Documentation

* [last_modified s3 with Python](https://stackoverflow.com/questions/9679344/how-can-i-get-last-modified-datetime-of-s3-objects-with-boto)
* [Using SES with Python](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-using-sdk-python.html)
* [Boto3 - S3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/migrations3.html)