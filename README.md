# S3 Monitor

S3 Monitor intend to check the last object date in AWS S3 bucket, and if its older than today, send alerting email via AWS Simple Email Service (SES).

I'm using this to monitor my effective backup of my home automation system and be alerted on any backup issue.

## Technical details

* Uses AWS Lambda function (Python)
* Rely on AWS Lambda layer for boto3 and botocore
* Scheduled Lambda (daily) with CloudWatch Events
* Uses AWS Simple Email Service (SES) for Emails Notifications

## Installation

Using [AWS Serverless Application Model (SAM)](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md)

### Build

```bash
$ make layer
$ make package
```

### Deploy

```bash
$ make deploy env=<your_env>
```

### Cleaning
```bash
$ make cleaning
```

## Documentation

* [last_modified s3 with Python](https://stackoverflow.com/questions/9679344/how-can-i-get-last-modified-datetime-of-s3-objects-with-boto)
* [Using SES with Python](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/send-using-sdk-python.html)
* [Boto3 - S3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/migrations3.html)
* [SAM documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-template.html#serverless-sam-template-function)