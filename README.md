# S3 Monitor

S3 Monitor intend to check the last object(key) creation date in S3, and if its older than defined date, send email alerting.

## Technical details

* Using AWS Lambda (Python)
* Scheduled (daily) with cron
* Uses AWS Simple Email Service for Notifications

## Used Documentation

* https://stackoverflow.com/questions/9679344/how-can-i-get-last-modified-datetime-of-s3-objects-with-boto
* https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-using-sdk-python.html