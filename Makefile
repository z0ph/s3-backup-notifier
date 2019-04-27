
help:
	@echo "layer - prepare the layer for boto3"
	@echo "package - prepare the package for s3 monitor"
	@echo "deploy - deploy the lambda function"
	@echo "packloy - package and deploy"
	@echo "clean - clean the build folder"
	@echo "clean-layer - clean the layer folder"
	@echo "cleaning - clean build and layer folders"

S3_BUCKET ?= zoph-s3monitor-artifacts
AWS_REGION ?= eu-west-1
env ?= dev

package: clean
	@echo "Consolidating python code in ./build"
	mkdir -p build

	cp -R *.py ./build/

	@echo "zipping python code, uploading to S3 bucket, and transforming template"
	aws cloudformation package \
			--template-file sam-s3monitor.yml \
			--s3-bucket ${S3_BUCKET} \
			--output-template-file build/template-lambda-s3monitor.yml

	@echo "Copying updated cloud template to S3 bucket"
	aws s3 cp build/template-lambda-s3monitor.yml 's3://${S3_BUCKET}/template-lambda-s3monitor.yml'

layer: clean-layer
	pip install \
			--isolated \
			--disable-pip-version-check \
			-Ur requirements.txt -t ./layer/

clean-layer:
	@rm -fr layer/
	@rm -fr dist/
	@rm -fr htmlcov/
	@rm -fr site/
	@rm -fr .eggs/
	@rm -fr .tox/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '.DS_Store' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr htmlcov/
	@rm -fr site/
	@rm -fr .eggs/
	@rm -fr .tox/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '.DS_Store' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

cleaning: clean clean-layer

deploy:
	aws cloudformation deploy \
			--template-file build/template-lambda-s3monitor.yml \
			--region ${AWS_REGION} \
			--stack-name "s3monitor-${env}" \
			--parameter-overrides env=${env} \
			--capabilities CAPABILITY_IAM \
			--no-fail-on-empty-changeset

packloy:
	aws-vault exec admin -- make package env=${env} && aws-vault exec admin -- make deploy env=${env}