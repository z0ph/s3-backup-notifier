# S3 Backup Notifier :envelope:

s3 backup notifier intends to `daily` check the last object date in an AWS S3 bucket, and if it's older than today, send alerting email via AWS Simple Email Service (SES).

I'm using this to monitor the effectiveness of backup of my home automation systems and be alerted on any backup related issue.

## Technical details

> Fully serverless.

* Uses AWS Lambda function (Python)
* Rely on AWS Lambda layer for `boto3` and `botocore`
* Scheduled Lambda (`daily`) using CloudWatch Events
* Uses AWS Simple Email Service (SES) for Emails Notifications

## Installation

### Requirements

* Configure AWS Credentials (prefer [aws-vault](https://github.com/99designs/aws-vault))
* Create a bucket called: `<project_name>-artifacts`

> Its using [AWS Serverless Application Model (SAM)](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md)

### Build

Build layer, and Lambda function package.

```bash
$ make layer
$ make package
```

### Deploy

Deploy CloudFormation stack.

```bash
$ make deploy PROJECT=<project_name> ENV=<your_env> MONITORING_BUCKET=<bucket_to_monitor> S3_PREFIX=<s3_prefix>
```

### Cleaning

Remove unused folders and files after the deployment of your the stack.

```bash
$ make cleaning
```
