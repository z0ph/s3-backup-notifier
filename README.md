# s3-monitor

`s3-monitor` is a small serverless app that checks an S3 prefix once a day and emails you (via SES) if the most recent object under that prefix is not from today. Useful for backup-freshness alerting (home automation snapshots, database dumps, etc.).

## How it works

- A single AWS Lambda function (Python 3.12, arm64) lists the configured bucket/prefix and finds the object with the most recent `LastModified` timestamp.
- If that date is **today**, it stays silent.
- If it is **stale** or there are **no objects at all**, it sends an SES email to the configured recipient list.
- A CloudWatch alarm on the function's `ERROR` log lines publishes to an SNS topic so a single on-call address gets paged if the function itself fails.
- A daily EventBridge schedule (via SAM's `Schedule` event) triggers the function. The schedule can be disabled per environment via the `CRONENABLED` parameter.

## Requirements

- AWS account with **SES** in production mode (or sandbox if `SENDER` and all `RECIPIENTS` are verified).
- AWS CLI v2 and [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) installed locally.
- Python 3.12 (for tests/lint only; the runtime ships its own).
- Configured AWS credentials. [`aws-vault`](https://github.com/99designs/aws-vault) recommended.

## Deploy

The only supported deploy path is SAM. Configuration for the `dev` and `prod` stacks lives in [`samconfig.toml`](samconfig.toml).

The first time, you'll need to supply the SES-related parameters either via `--parameter-overrides` or by editing `samconfig.toml`. The mandatory parameters are:

| Parameter          | Description                                                       |
| ------------------ | ----------------------------------------------------------------- |
| `MONITORINGBUCKET` | The bucket to inspect                                             |
| `S3PREFIX`         | Key prefix to scope the listing (use empty string for whole bucket) |
| `SENDER`           | SES-verified sender address                                       |
| `RECIPIENTS`       | Whitespace-separated list of SES recipient addresses              |
| `ALERTRECIPIENT`   | Single email subscribed to the function's error SNS topic         |

```bash
make build
make deploy ENV=dev \
  # or: sam deploy --config-env dev \
  #   --parameter-overrides "MONITORINGBUCKET=..." "SENDER=..." \
  #                         "RECIPIENTS='a@x b@y'" "ALERTRECIPIENT=ops@x"
```

To tear a stack down:

```bash
make destroy ENV=dev
```

## Develop

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

make lint   # ruff check .
make test   # pytest
```

Tests run against `moto` and do not touch AWS.

## License

MIT. See [LICENSE](LICENSE).
