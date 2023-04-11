# Week 6 — Deploying Containers

Contents:
1. [ECS Security Considerations](#ecs-security-considerations)
2. [Fargate Technical Questions]
3. [Provision ECS Cluster](#provision-ecs-cluster)
4. [Create ECR repo and push image for backend-flask](#create-ecr-repo-and-push-image-for-backend-flask)

## ECS Security Considerations
  Watch ECS Security by Ashish	https://www.youtube.com/watch?v=zz2FQAk1I28&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=57

## Fargate Technical Questions
  Watch Fargate Technical Questions with Maish (Not yet uploaded)
  
## Provision ECS Cluster
[stream link](https://www.youtube.com/watch?v=QIZx2NhdCMI&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=58)

### Create script to test connection to RDS :white_check_mark:
1. go to backend-flask/bin/db folder and create a new script 'test' to test connection to RDS in AWS:
```python
#!/usr/bin/env python3

import psycopg
import os
import sys

connection_url = os.getenv("CONNECTION_URL")

conn = None
try:
  print('attempting connection')
  conn = psycopg.connect(connection_url)
  print("Connection successful!")
except psycopg.Error as e:
  print("Unable to connect to the database:", e)
finally:
  conn.close()
```
2. make it executable with ```chmod u+x``` command
3. note that my CONNECTION_URL = PROD_CONNECTION_URL
4. remember to update GITPOD_UP and run update security group script
5. run ```./bin/db/test``` script from backend-flask folder
6. expected response:
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/db/test
attempting connection
Connection successful!
```


### Implement health check for backend container :white_check_mark:
1. go to app.py
2. add these lines above rollbar test:
```python
@app.route('/api/health-check')
def health_check():
  return {'success': True}, 200
```
3. create new script backend-flask/bin/flask/health-check:
```python
#!/usr/bin/env python3

import urllib.request

try:
  response = urllib.request.urlopen('http://localhost:4567/api/health-check')
  if response.getcode() == 200:
    print("[OK] Flask server is running")
    exit(0) # success
  else:
    print("[BAD] Flask server is not running")
    exit(1) # false
# This for some reason is not capturing the error....
#except ConnectionRefusedError as e:
# so we'll just catch on all even though this is a bad practice
except Exception as e:
  print(e)
  exit(1) # false
```
4. make it executable with ```chmod u+x``` command
5. Docker shall not have Curl in our container for security reasons
6. run ```./bin/flask/health-check```
7. Andrew had error '111 Connection refused' watched, so did I:
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/flask/health-check
<urlopen error [Errno 111] Connection refused>
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ 
```

### Create CloudWatch Log Group :white_check_mark:

1. got to AWS CloudWatch console
2. run these commands in CLI (or CloudShell):
```
aws logs create-log-group --log-group-name "/cruddur/fargate-cluster"
aws logs put-retention-policy --log-group-name "/cruddur/fargate-cluster" --retention-in-days 1
```
3. retention days set to 1 for the cost reason. The lowest it can be!
4. go back to the AWS CloudWatch console and check that '/cruddur/fargate-cluster' log group appeared

### Create ECS Cluster :white_check_mark:
1. run these commands in CLI (CloudShell):
```
aws ecs create-cluster \
--cluster-name cruddur \
--service-connect-defaults namespace=cruddur
```
2. Check in AWS console that the cluster is created and new tasks are not running yet, i.e. no spend concern just yet
3. no need for security groups for now


	
## Create ECR repo and push image for backend-flask  
[stream link] (https://www.youtube.com/watch?v=QIZx2NhdCMI&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=58)
We are going to create 3 repos:

#### Base Image Python :white_check_mark:
1. create a repository for base python image
```
aws ecr create-repository \
  --repository-name cruddur-python \
  --image-tag-mutability MUTABLE
```
2. our backend container references python:3.10-slim-buster from DockerHub. We are going to pull this image and then push it to ECR
3. we keep tags mutable for easier life but we would not do this for real production app
4. we will login to ECR with this command:
```
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
```
5 expected reult from the terminal:
```
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
WARNING! Your password will be stored unencrypted in /home/gitpod/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded
```
6. next we need to map URI to ECR:
```
export ECR_PYTHON_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/cruddur-python"
echo $ECR_PYTHON_URL
```
7. keep in in mind that our backend container uses Python 3.10
8. pull image: ```docker pull python:3.10-slim-buster```
9. terminal output:
```
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ docker pull python:3.10-slim-buster
3.10-slim-buster: Pulling from library/python
3689b8de819b: Already exists 
af8cd5f36469: Already exists 
74adefb035bf: Already exists 
7d3f13b19e92: Already exists 
ee5147252e65: Already exists 
Digest: sha256:7d6283c08f546bb7f97f8660b272dbab02e1e9bffca4fa9bc96720b0efd29d8e
Status: Downloaded newer image for python:3.10-slim-buster
docker.io/library/python:3.10-slim-buster
```
10. run ```docker images``` to see the image
11. tag image: ```docker tag python:3.10-slim-buster $ECR_PYTHON_URL:3.10-slim-buster```
12. push image: ```docker push $ECR_PYTHON_URL:3.10-slim-buster```
13. got to ECR console, navigate inside the cruddur repository and check that this image is present
14. next we need to set URI to pull the image in our Dockerfile like so ```FROM ${ECR_PYTHON_URL}:3.10-slim-buster```
15. ```docker compose up backend-flask db```
16. go to cruddur back-end container url and append with ```/api/health-check```. Health check shall be successful:
```
{
  "success": true
}
```


	
## Deploy Backend Flask app as a service to Fargate	
https://www.youtube.com/watch?v=QIZx2NhdCMI&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=58
	
## Create ECR repo and push image for fronted-react-js	
  https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59
  
## Deploy Frontend React JS app as a service to Fargate
https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59

## Provision and configure Application Load Balancer along with target groups
https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59
	
## Manage your domain useing Route53 via hosted zone	
https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59
	
## Create an SSL cerificate via ACM	
https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59
	
## Setup a record set for naked domain to point to frontend-react-js
https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59
	
## Setup a record set for api subdomain to point to the backend-flask
https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59
	
## Configure CORS to only permit traffic from our domain	
https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59
	
## Secure Flask by not running in debug mode	
https://www.youtube.com/watch?v=9OQZSBKzIgs&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=60

## Implement Refresh Token for Amazon Cognito	
https://www.youtube.com/watch?v=LNLP2dxa5EQ&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=63
	
## Refactor bin directory to be top level	
https://www.youtube.com/watch?v=HyJOjBjieb4&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=62
	
## Configure task defintions to contain x-ray and turn on Container Insights
https://www.youtube.com/watch?v=G_8_xtS2MsY&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=64
	
## Change Docker Compose to explicitly use a user-defined network
https://www.youtube.com/watch?v=G_8_xtS2MsY&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=64
	
## Create Dockerfile specfically for production use case
https://www.youtube.com/watch?v=G_8_xtS2MsY&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=64
	
## Using ruby generate out env dot files for docker using erb templates
https://www.youtube.com/watch?v=G_8_xtS2MsY&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=64
