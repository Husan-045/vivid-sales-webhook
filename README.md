# Python AWS Lambda App that will be triggered by event bridge
This is a project template for a python application that will be triggered by event bridge.

# Technology Stack
* Python 3.10
* Docker
* Terraform

# Running Locally
1. Start a local redis: `docker run --name redis-cache --rm -p 6379:6379 redis:7`
2. Configure .env to something like this:
```
ENVIRONMENT=staging
CLOUDWATCH_NAMESPACE=ticketboat-email-router
AWS_DEFAULT_REGION=us-east-1
OPENAI_API_KEY=<your open ai key>
AWS_PROFILE=ticketboat
SNOWFLAKE_DATABASE=ticketboat_staging
SNOWFLAKE_PASSWORD=<email_processor snowflake password>
REDIS_ADDRESS=host.docker.internal
REDIS_PORT=6379

```


# Using this Template

### Clone the project
```
git clone https://<your user>@bitbucket.org/nrd-tech/python-aws-lambda-basic.git my-project
cd my-project
```

### Initialize a new git repo for your project
```
rm -fR .git venv .idea
git init
git add .
git commit -m 'init'
```

### Configure
* Edit the _config.sh file
  * Each config is a little different per application but at a minimum you will need to change:
    * APP_IDENT
    * TERRAFORM_STATE_BUCKET
* Commit your changes to git
```
git commit -a -m 'updated config'
```

### Set up bitbucket pipeline deployment
* Push your git project up into a new Bitbucket project
* Navigate to your project on Bitbucket
  * Click Repository Settings
  * Click Pipelines->Settings
    * Click Enable Pipelines
  * Click Pipelines->Repository Variables
    * In order to give Bitbucket access to deploy to your AWS environment 
      you must enter the following variables with credentials that have 
      access to create services in your AWS account.
      * AWS_ACCESS_KEY_ID
      * AWS_SECRET_ACCESS_KEY
      * AWS_DEFAULT_REGION (example: us-west-2)

### Deploy to Staging
```
git checkout -b staging
git push --set-upstream origin staging
```

### Deploy to Production
```
git checkout -b production
git push --set-upstream origin production
```

# Un-Deploying
1. Before you can have Terraform un-deploy the project you must manually
   remove all the Images in the ECR repository. This is a safety mechanism
   to make sure you don't blow away images accidentally that you need.
2. Navigate to the Bitbucket project website
3. Click Pipelines in the left nav menu
4. Click Run pipeline button
5. Choose the branch you want to un-deploy
6. Choose the appropriate un-deploy Pipeline
   * un-deploy-staging
   * un-deploy-production
7. Click Run

# Sample pip.conf file to place in your ./venv directory
```
[global]
index-url = https://pypi.org/simple

[list]
format = columns

[freeze]
exclude-editable = yes

[install]
upgrade = yes
```

# Run docker image locally
```
aws ecr get-login-password \
      --region us-west-2 | \
      docker login \
        --username AWS \
        --password-stdin 482370276428.dkr.ecr.us-west-2.amazonaws.com/myapp_lambda_repository

docker run --rm -p 9000:8080 -it 482370276428.dkr.ecr.us-west-2.amazonaws.com/myapp_lambda_repository:latest 

docker run --platform linux/amd64 \
  -e AWS_ACCESS_KEY_ID=asdf \
  -e AWS_SECRET_ACCESS_KEY=qwer \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e ENVIRONMENT=staging \
  -e APP_IDENT=my_app \
  -e CLOUDWATCH_MONITOR_NAMESPACE=my_namespace \
  -e DOCKER_LAMBDA_USE_STDIN=1 \
  -p 9000:8080 \
  nic-test

curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'

```

# Inspect docker image
```
alias dive="docker run -ti --rm  -v /var/run/docker.sock:/var/run/docker.sock wagoodman/dive"
dive 482370276428.dkr.ecr.us-west-2.amazonaws.com/myapp_lambda_repository:latest
```
