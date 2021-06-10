# S3 Backup Notifier :envelope:

![Deploy s3-backup-notifier](https://github.com/z0ph/s3-backup-notifier/workflows/Deploy%20s3-backup-notifier/badge.svg?branch=master)

S3 backup notifier intends to `daily` check the last object date in an AWS S3 bucket, and if it's older than today, send alerting email via AWS Simple Email Service (SES).

I'm using this to monitor the effectiveness of backup of my home automation systems and be alerted on any failed backup intend.

## Technical details

> Fully serverless.

* Uses AWS Lambda function (Python)
* Scheduled Lambda (`daily`) using CloudWatch Events
* Uses AWS Simple Email Service (SES) for Emails Notifications

Nb: deployment for my own usage is done using Github Actions, you can check the associated [workflow](.github/workflows/main.yml).

## Installation

### Requirements

* Configure AWS Credentials (prefer [aws-vault](https://github.com/99designs/aws-vault))
* Create a bucket called: `<project_name>-artifacts` (Prefer versioned and encrypted)

> Its using [AWS Serverless Application Model (SAM)](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md)

### :woman_factory_worker: Build & Deploy

Build AWS Lambda function package.

```bash
$ make package
```

#### Deploy CloudFormation stack

> Nb: RECIPIENTS var is space-separated

```bash
$ make deploy \
    PROJECT=<your_project_name> \
    ENV=<your_env> \
    MONITORING_BUCKET=<bucket_to_monitor> \
    S3_PREFIX=<s3_prefix> \
    SENDER=<sender_email> \
    RECIPIENTS='<recipient_email1> <recipient_email2>' \
    AWS_REGION='<your_aws_region>'
```

### Cleaning

Remove unused folders and files after the deployment of your stack.

```bash
$ make clean
```

### Destroy Stack

```bash
$ make tear-down
```
