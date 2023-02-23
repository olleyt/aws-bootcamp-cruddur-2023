# Week 1 — App Containerization

## Mandatory Tasks - Completed 

### Confirmed that PostgreSQL Container Works as expected

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

## New Learnings

### Docker and Docker Compose
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

This can be probably rectified with .gitpod.yml by adding ms-azuretools.vscode-docker into extensions

### Docker compose file was in incorrect folder

When I ran compose up first time from the left navigation pane, Docker did not produce working containers and both containers were in red status. 
* _Trobleshooting steps:_
    * I looked into the logs and the error was saying that FLASK_APP variable is not set and some files are not found. 

* _Solution:_
    * The problem was that I created docker-compose not on the root but inside the the front-end folder when clicked adding file on the left side pane! Sometimes I love bash commands better than point & click approach. It was such a baffling and silly error to create file in a wrong place. 

* _Status:_
    * It's all working now. 
