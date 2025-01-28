# S3 Backup Notifier

S3 Backup Notifier is a serverless application designed to monitor a specific prefix in Amazon S3 buckets. It checks daily for the latest object in a specified S3 bucket and sends an alert email via AWS Simple Email Service (SES) if no new backup is detected for the current day.

## Use Case

This tool is ideal for monitoring the effectiveness of backup systems, such as home automation systems, and ensuring timely alerts for any failed backup attempts from outside.

## Technical Details

- **Serverless Architecture**: Utilizes AWS Lambda functions written in Python.
- **Scheduled Execution**: Lambda functions are triggered daily using AWS CloudWatch Events.
- **Email Notifications**: Alerts are sent using AWS Simple Email Service (SES).

> Note: Deployment for personal use is automated using GitHub Actions. Refer to the associated [workflow](.github/workflows/main.yml).

## Installation

### Requirements

- **AWS Credentials**: Configure your AWS credentials. It's recommended to use [aws-vault](https://github.com/99designs/aws-vault) for secure storage.
- **S3 Bucket**: Create a bucket named `<project_name>-artifacts`. It's advisable to enable versioning and encryption for security.

> The project uses the [AWS Serverless Application Model (SAM)](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md) for deployment.

### :woman_factory_worker: Build & Deploy

#### Build AWS Lambda Function Package

```bash
$ make package
```

#### Deploy CloudFormation Stack

> Note: The `RECIPIENTS` variable should be space-separated.

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

Remove unused folders and files after deploying your stack.

```bash
$ make clean
```

### Destroy Stack

To remove the deployed stack, use the following command:

```bash
$ make tear-down
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
