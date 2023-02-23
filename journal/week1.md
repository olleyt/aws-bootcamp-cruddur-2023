# Week 1 — App Containerization


## Mandatory Tasks - Completed

### Spending Considerations
Watcked Chirag's Week 1 - [Spending Considerations](https://www.youtube.com/watch?v=OAMHu1NiYoI&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=24)

Notes: 
* remember to stop a workspace when not used to keep under the free tier
* check billing page for remaining credits regularly
* delete unused workspaces to reduce clatter

### Container Security Considerations
Watched Ashish's Week 1 - [Container Security Considerations](https://www.youtube.com/watch?v=OjZz4D0B-cA&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=25)

Notes: 
* running Snyk on Cruddur repository identified 6 critical vulnerabilities related mostly to outdated openssl and Node. More on that in 'Stretch Challenges' section 
* try to run Snyk on container images as a stretch challenge
* try Inspector when we progress pushing Docker impages to ECR


### Completed Technical Tasks - Code Changes Committed
These tasks were completed without issues following along the videos and committing code changes from GitPod.
The commits can be found in the git history for the main branch.

* [Containerized Application (Dockerfiles, Docker Compose)](https://www.youtube.com/watch?v=zJnNe5Nv4tE&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=22)
* [Documented the Notification Endpoint for the OpenAI Document](https://www.youtube.com/watch?v=k-_o0cCpksk&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=27)
* [Wrote a Flask Backend Endpoint for Notifications](https://www.youtube.com/watch?v=k-_o0cCpksk&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=27)
* [Wrote a React Page for Notifications](https://www.youtube.com/watch?v=k-_o0cCpksk&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=27)

These additional tasks for PostgreSQL and DynamoDB contrainers verification are discussed in the two sections below.
### [Confirmed that PostgreSQL Container Works as expected](https://www.youtube.com/watch?v=CbQNMaa6zTg&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=28)

Use command  ``` psql -Upostgres -h localhost``` where -U<username> for the username and -h as localhost parameters   to check if the PostreSQL client is up and working.

The expected output:

```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ psql -Upostgres -h localhost
Password for user postgres: 
psql (13.10 (Ubuntu 13.10-1.pgdg20.04+1))
Type "help" for help.

postgres=# \dl
      Large objects
 ID | Owner | Description 
----+-------+-------------
(0 rows)

postgres=# \q
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ 
```

### [Confirmed that DynamoDB Container Works](https://www.youtube.com/watch?v=CbQNMaa6zTg&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=28)
      
As the Cruddur AWS user was configured with explicit polocies for the required actions only, a new policy *cruddur_dynamodb_policy_cli* to interact with DynamoDB had to be added first:
```json
   {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "dynamodb:GetRecords",
            "Resource": "arn:aws:dynamodb:*:<ACCOUNT_ID>:table/*/stream/*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "dynamodb:CreateTable",
                "dynamodb:PutItem",
                "dynamodb:DescribeTable",
                "dynamodb:DeleteItem",
                "dynamodb:GetItem",
                "dynamodb:Scan",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteTable",
                "dynamodb:UpdateTable"
            ],
            "Resource": "arn:aws:dynamodb:*:<ACCOUNT_ID>:table/*"
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": "dynamodb:ListTables",
            "Resource": "*"
        }
    ]
}
```      

Then this policy was attached by Cruddur AWS Admin to the AWS CLI user using IAM console.
Expected outcome: the cruddur_dev user shall have 5 policies attached directly as we follow the principal of least priviledge:
1. cruddur_create_budget
2. cruddur_create_sns_topic
3. cruddur_dynamodb_policy_cli
4. cruddur_put_cloud_watch_alarm_metric
5. cruddur-sts-get-caller-identity

      
#### Confirmed that DynamoDB is accessible locally on the Docker container

At this point local DynamoDB accessibility can be check with AWS CLI commands. This [list of commands](https://dynobase.dev/dynamodb-cli-query-examples/) can be useful for smoke tests.
      
As we will start interact with DynamoDB in a few weeks, it is enough to list tables for a smoke test with this command: 
```bash
      aws dynamodb list-tables
```      
Expected result as there are no tables at this point:
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ aws dynamodb list-tables
{
    "TableNames": []
}
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ 
```      
      
## My learnings for this week
This part is written in a story telling mode to bore you less as you read it and reflect on my personal experiences and challenges.

### Time management and personal efficiency
* The most efficient way to slice and dice and understand material _for me_ was writing it down on a paper in a small achievable tasks.
* Story telling in personal voice keep me a lot more engaged with the project as it is a fun activity to do. 
* Self reflecting increases depth of understanding and makes new material more digestable. 
      
### Spelling of the word priviledge
Had to make it fun to memorise spelling of this word:
      ```Remember first two vowels are i and last 2 are e.```
      
### Docker and Docker Compose
      I am fairly new to Docker and it was my first experience with creating Docker files and composing images. 
      I realised that more learnings required for me to progress with stretch challenges for this week.
      Nevertheless, I was able to finish all the mandatory assignments without issues from the first time

### GitPod Custom Image
This week I learned from [article posted by Jason Paul](https://www.linuxtek.ca/2023/02/21/diving-deeper-gitpod-cloud-development-environment/) that GitPod persists only /workspace and managing dependencies and longer running installations shall be done via customizing docker file for GitPod: .gitpod.Dockerfile

That helped to resolved missing AWS CLI after each stop / start of my GitPod environment.

### Open API
This week was a great opportunity to learn how to design and document REST APIs with OpenAPI specification (former Swagger).
The OpenAPI spec advatntage are:
* it can be easily loaded into AWS API Gateway and used in CloudFormation which in turn can save a ton of development effort
* it is a unified format that different teams / developers can learn and follow and be on the same page
* it has wonderful apps such as Readme to create interactive visual documentation 

## Challenges I faced and how I overcome them

### GitPod not persisting AWS CLI installations between start stops

Prebuild was added to .gitpod.yml
```bash
github:
  prebuilds:    
    master: true    
    branches: true    
    pullRequests: true    
    pullRequestsFromForks: false    
    addCheck: true    
    addComment: false    
    addBadge: false
```

AWS CLI needed to be reinstalled even with activating prebuild on GitPod like so:
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ aws --version
bash: aws: command not found
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ cd ..
gitpod /workspace $ sudo ./aws/install
You can now run: /usr/local/bin/aws --version
gitpod /workspace $ aws --version
aws-cli/2.10.2 Python/3.9.11 Linux/5.15.0-47-generic exe/x86_64.ubuntu.20 prompt/off
gitpod /workspace $ 
```

### GitPod did not have Docker extension preinstalled

This was rectified in .gitpod.yml by adding ms-azuretools.vscode-docker into extensions

### Docker compose file was in incorrect folder

When I ran compose up first time from the left navigation pane, Docker did not produce working containers and both containers were in red status. 
* _Trobleshooting steps:_
    * I looked into the logs and the error was saying that FLASK_APP variable is not set and some files are not found. 

* _Solution:_
    * The problem was that I created docker-compose not on the root but inside the the front-end folder when clicked adding file on the left side pane! Sometimes I love bash commands better than point & click approach. It was such a baffling and silly error to create file in a wrong place. 

* _Status:_
    * It's all working now. 
