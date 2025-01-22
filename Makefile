.DEFAULT_GOAL := help

# Project Information
PROJECT ?= s3-monitor
DESCRIPTION := S3 Backup Notifier

# AWS and S3 Configuration
S3_BUCKET ?= ${PROJECT}-artifacts
MONITORING_BUCKET := backup.bucket
RECIPIENTS := david@doe.com
SENDER := john@doe.com
S3_PREFIX := MyPrefix
AWS_REGION ?= eu-west-1
ENV ?= dev

# Phony targets
.PHONY: help package deploy clean tear-down

# Help target to display available commands
help:
	@echo "${PROJECT}"
	@echo "${DESCRIPTION}"
	@echo ""
	@echo "	package - prepare the package"
	@echo "	deploy - deploy the lambda function"
	@echo "	clean - clean the build folder"

# Package target to prepare the deployment package
package: clean
	@echo "Consolidating python code in ./build"
	mkdir -p build sam-template
	cp -R ./python/*.py ./build/

	@echo "Zipping python code, uploading to S3 bucket, and transforming template"
	aws cloudformation package \
		--template-file template.yml \
		--s3-bucket ${S3_BUCKET} \
		--output-template-file ./sam-template/sam.yml

	@echo "Copying updated cloud template to S3 bucket"
	aws s3 cp ./sam-template/sam.yml "s3://${S3_BUCKET}/"

# Deploy target to deploy the application
deploy:
	aws cloudformation deploy \
		--template-file ./sam-template/sam.yml \
		--region ${AWS_REGION} \
		--stack-name "${PROJECT}-${ENV}" \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides \
			ENV=${ENV} \
			MONITORINGBUCKET=${MONITORING_BUCKET} \
			S3PREFIX=${S3_PREFIX} \
			PROJECT=${PROJECT} \
			RECIPIENTS=${RECIPIENTS} \
			SENDER=${SENDER} \
			AWSREGION=${AWS_REGION} \
		--no-fail-on-empty-changeset

# Clean target to remove build artifacts
clean:
	@rm -fr build/ dist/ htmlcov/ site/ .eggs/ .tox/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '.DS_Store' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

# Tear-down target to delete the stack
tear-down:
	@read -p "Are you sure that you want to destroy stack '${PROJECT}-${ENV}'? [y/N]: " sure && [ $${sure:-N} = 'y' ]
	aws cloudformation delete-stack --stack-name "${PROJECT}-${ENV}"
