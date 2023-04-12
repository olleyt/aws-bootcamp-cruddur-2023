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


	
## Create ECR repo and push image for backend-flask  :white_check_mark:
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

#### Flask image :white_check_mark:

1.create Repo
```
  aws ecr create-repository \
  --repository-name backend-flask \
  --image-tag-mutability MUTABLE
```  
2. set URL
```
export ECR_BACKEND_FLASK_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/backend-flask"
echo $ECR_BACKEND_FLASK_URL
```
3. build Image, note that I had to put explicit value of ECR_PYTHON_URL into the Docker file
```
docker build -t backend-flask .
```
4. tag Image
```
docker tag backend-flask:latest $ECR_BACKEND_FLASK_URL:latest
```
5. push Image
```
docker push $ECR_BACKEND_FLASK_URL:latest
```
6. Fargate will look for 'latest' tag but we probably shall use tags in real DevOps life

	
## Deploy Backend Flask app as a service to Fargate	
[stream link](https://www.youtube.com/watch?v=QIZx2NhdCMI&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=58)
1. Login to the AWS ECS console
2. go to our cruddur cluster. You'll see tabs 'Services' and 'Tasks'. The difference is that service is continiously running whereas tasks kills itself when it finished its job (better suited for batch jobs). We want a service because we are running a web application.
3. we need to create a task definition that is similar to Docker file that defines how to build a cintainer.
4. AWS will take care of envoy proxy
5. task role defines permission that container will have when it is running whereas execution role is when task is executed
6. we will use awsvpc mode to have ENI automatically assigned
7. we shall keep cpu and memory ratio as 1:2 (256Mb : 512Mb)
8. create service-assume-role-execution-policy.json
```json
{
    "Version":"2012-10-17",
    "Statement":[{
        "Action":["sts:AssumeRole"],
        "Effect":"Allow",
        "Principal":{
          "Service":["ecs-tasks.amazonaws.com"]
      }}]
  }  
```
9. create service-execution-policy.json, note that ${AWS::AccountId} shall be substituted with account id value otherwise CLI throws error
```json
{
    "Version":"2012-10-17",
    "Statement":[{
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameters",
        "ssm:GetParameter"
      ],
      "Resource": "arn:aws:ssm:us-east-1:${AWS::AccountId}:parameter/cruddur/backend-flask/*"
    }]
  }
```
10. run the role creation command in CLI:
```
aws iam create-role \    
--role-name CruddurServiceExecutionRole  \   
--assume-role-policy-document file://aws/policies/service-assume-role-execution-policy.json
```
11. create ssm parameters via CLI:
```
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_ACCESS_KEY_ID" --value $AWS_ACCESS_KEY_ID
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/AWS_SECRET_ACCESS_KEY" --value $AWS_SECRET_ACCESS_KEY
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/CONNECTION_URL" --value $PROD_CONNECTION_URL
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/ROLLBAR_ACCESS_TOKEN" --value $ROLLBAR_ACCESS_TOKEN
aws ssm put-parameter --type "SecureString" --name "/cruddur/backend-flask/OTEL_EXPORTER_OTLP_HEADERS" --value "x-honeycomb-team=$HONEYCOMB_API_KEY"
```
12. go to AWS SSM console, navigate to Parameter Store and check if they all set correctly
13. create task role:
```json
aws iam create-role \
    --role-name CruddurTaskRole \
    --assume-role-policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[\"sts:AssumeRole\"],
    \"Effect\":\"Allow\",
    \"Principal\":{
      \"Service\":[\"ecs-tasks.amazonaws.com\"]
    }
  }]
}"
```
14. create policy:
```
aws iam put-role-policy \
  --policy-name SSMAccessPolicy \
  --role-name CruddurTaskRole \
  --policy-document "{
  \"Version\":\"2012-10-17\",
  \"Statement\":[{
    \"Action\":[
      \"ssmmessages:CreateControlChannel\",
      \"ssmmessages:CreateDataChannel\",
      \"ssmmessages:OpenControlChannel\",
      \"ssmmessages:OpenDataChannel\"
    ],
    \"Effect\":\"Allow\",
    \"Resource\":\"*\"
  }]
}
"
```
15. add cloudWatch and X-ray permissions:
```
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess --role-name CruddurTaskRole
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess --role-name CruddurTaskRole
```
16. under aws folder create a new one called 'task-definition'
17. create a new file called backend-flask.json inside of this new folder
18. register task definition and make sure these are defined on the task level:
```
"cpu": "256",
  "memory": "512",
  "requiresCompatibilities": [ 
    "FARGATE" 
  ],
```
run command in CLI:
```
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json
```
19. go to ECS console and check that task definition was created
20. get dafault VPC by running this command:
```bash
export DEFAULT_VPC_ID=$(aws ec2 describe-vpcs \
--filters "Name=isDefault, Values=true" \
--query "Vpcs[0].VpcId" \
--output text)
echo $DEFAULT_VPC_ID
```
21. create security group:
```bash
export CRUD_SERVICE_SG=$(aws ec2 create-security-group \
  --group-name "crud-srv-sg" \
  --description "Security group for Cruddur services on ECS" \
  --vpc-id $DEFAULT_VPC_ID \
  --query "GroupId" --output text)
echo $CRUD_SERVICE_SG
```
22. open port 80 for this security group:
```bash
aws ec2 authorize-security-group-ingress \
  --group-id $CRUD_SERVICE_SG \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
```
23. create Fargate service in the AWS ECS console (GUI)
24. then we found out that our Fargate role missed get authorizarion token permission for ECR, so we need to add this permission to the role CruddurServiceExecutionRole
25. Note: in my case I had to delete CloudFormation stack that created ECS service and the service itself was rolled back. Andrew forced the service redeployment.
26. next we needed to add cloudwatch access to create a log stream added to the same role and we added CloudWatchFullAccess policy to the role
27. then we had error (ACCOUNT_ID replaced the real value):
```
CannotPullContainerError: pull image manifest has been retried 1 time(s): failed to resolve ref ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/backend-flask:latest: pulling from host ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com failed with status code [manifests latest]: 403 Forbidden
```
28. then we needed to add more ECR permission to the same policy CruddurServiceExecutionPolicy as explained [here](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-policy-examples.html)
29. now the service is runninng but the health check status is 'unknown'
30. we need to install SSM plugin on GitPod:
```
curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_64bit/session-manager-plugin.deb" -o "session-manager-plugin.deb"
sudo dpkg -i session-manager-plugin.deb
```
31. verify it is working by running this command ```session-manager-plugin```
32. connect to the container:
```
aws ecs execute-command  \
--region $AWS_DEFAULT_REGION \
--cluster cruddur \
--task 72e839665f8b4d33af8cac238f92a78a \
--container backend-flask \
--command "/bin/bash" \
--interactive
```
33. However, the error appeared:
```
An error occurred (InvalidParameterException) when calling the ExecuteCommand operation: The execute command failed because execute command was not enabled when the task was run or the execute command agent isn’t running. Wait and try again or run a new task with execute command enabled and try again.
```
34. go back to the ECS console and delete the service
35. create aws/json/service-backend-flask.json and
```json
{
    "cluster": "cruddur",
    "launchType": "FARGATE",
    "desiredCount": 1,
    "enableECSManagedTags": true,
    "enableExecuteCommand": true,
    "loadBalancers": [
      {
          "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:ACCOUNT_ID:targetgroup/cruddur-backend-flask-tg/TARGET_GROUP_ID",
          "containerName": "backend-flask",
          "containerPort": 4567
      }
    ],
    "networkConfiguration": {
      "awsvpcConfiguration": {
        "assignPublicIp": "ENABLED",
        "securityGroups": [
          "sg-0f712624a41a7ce84"
        ],
        "subnets": [
          "subnet-06377ea30fef723df",
          "subnet-07891b0180376d75c",
          "subnet-0419619de27cb7b35",
          "subnet-06ca0ac2341ac85c5",
          "subnet-0ef64c831e44e3e96",
          "subnet-016685aff57e51d74"
        ]
      }
    },
    "serviceConnectConfiguration": {
      "enabled": true,
      "namespace": "cruddur",
      "services": [
        {
          "portName": "backend-flask",
          "discoveryName": "backend-flask",
          "clientAliases": [{"port": 4567}]
        }
      ]
    },
    "propagateTags": "SERVICE",
    "serviceName": "backend-flask",
    "taskDefinition": "backend-flask"
  }
```
37. create ECS service via CLI
```
aws ecs create-service --cli-input-json file://aws/json/service-backend-flask.json
```
38 run command:
```
aws ecs execute-command  \
--region $AWS_DEFAULT_REGION \
--cluster cruddur \
--task 8764b10508954aa487fa8d4d4a8abfdd \
--container backend-flask \
--command "/bin/bash" \
--interactive
```
39. the terminal output shows that health check is running:
```
The Session Manager plugin was installed successfully. Use the AWS CLI to start a session.


Starting session with SessionId: ecs-execute-command-0251a3ff749509161
root@ip-xxx-xx-xx-xxx:/backend-flask# ./bin/flask/health-check
[OK] Flask server is running
root@ip-xxx-xx-xx-xxx:/backend-flask# 
```
40. create a new script 'connect-to-service 'in bin/ecs folder: 
```bash
#! /usr/bin/bash
if [ -z "$1" ]; then
  echo "No TASK_ID argument supplied eg ./bin/ecs/connect-to-backend-flask <task_id>"
  exit 1
fi
TASK_ID=$1

CONTAINER_NAME=backend-flask

echo "TASK ID : $TASK_ID"
echo "Container Name: $CONTAINER_NAME"

aws ecs execute-command  \
--region $AWS_DEFAULT_REGION \
--cluster cruddur \
--task $TASK_ID \
--container $CONTAINER_NAME \
--command "/bin/bash" \
--interactive
```
41. my cloudwatch logs show errors:
```

2023-04-11T19:12:23.493+10:00	127.0.0.1 - - [11/Apr/2023 09:12:23] "GET /api/health-check HTTP/1.1" 200 -

2023-04-11T19:12:31.878+10:00	Encountered an issue while polling sampling rules.

2023-04-11T19:12:31.878+10:00

Traceback (most recent call last):
Traceback (most recent call last):

2023-04-11T19:12:31.878+10:00
File "/usr/local/lib/python3.10/site-packages/urllib3/connection.py", line 174, in _new_conn

2023-04-11T19:12:31.878+10:00	conn = connection.create_connection(

2023-04-11T19:12:31.878+10:00	ConnectionRefusedError: [Errno 111] Connection refused

2023-04-11T19:12:31.878+10:00	During handling of the above exception, another exception occurred:

2023-04-11T19:12:31.878+10:00	Traceback (most recent call last):

2023-04-11T19:12:31.878+10:00	File "/usr/local/lib/python3.10/site-packages/botocore/httpsession.py", line 455, in send

2023-04-11T19:12:31.878+10:00	urllib_response = conn.urlopen(

2023-04-11T19:12:31.878+10:00	File "/usr/local/lib/python3.10/site-packages/urllib3/connectionpool.py", line 787, in urlopen

2023-04-11T19:12:31.878+10:00	retries = retries.increment(

2023-04-11T19:12:31.878+10:00	File "/usr/local/lib/python3.10/site-packages/urllib3/util/retry.py", line 525, in increment

2023-04-11T19:12:31.878+10:00	raise six.reraise(type(error), error, _stacktrace)

2023-04-11T19:12:31.878+10:00	File "/usr/local/lib/python3.10/site-packages/urllib3/packages/six.py", line 770, in reraise

2023-04-11T19:12:31.878+10:00	raise value

2023-04-11T19:12:31.878+10:00	File "/usr/local/lib/python3.10/site-packages/urllib3/connectionpool.py", line 703, in urlopen

2023-04-11T19:12:31.878+10:00	httplib_response = self._make_request(

2023-04-11T19:12:31.878+10:00	File "/usr/local/lib/python3.10/site-packages/urllib3/connectionpool.py", line 398, in _make_request

2023-04-11T19:12:31.878+10:00	conn.request(method, url, **httplib_request_kw)

2023-04-11T19:12:31.878+10:00	File "/usr/local/lib/python3.10/site-packages/urllib3/connection.py", line 244, in request

2023-04-11T19:12:31.878+10:00	super(HTTPConnection, self).request(method, url, body=body, headers=headers)

2023-04-11T19:12:31.878+10:00	File "/usr/local/lib/python3.10/http/client.py", line 1283, in request

2023-04-11T19:12:31.878+10:00	self._send_request(method, url, body, headers, encode_chunked)

2023-04-11T19:12:31.878+10:00	File "/usr/local/lib/python3.10/site-packages/botocore/awsrequest.py", line 94, in _send_request

2023-04-11T19:12:31.878+10:00	rval = super()._send_request(

2023-04-11T19:12:31.878+10:00	File "/usr/local/lib/python3.10/http/client.py", line 1329, in _send_request

2023-04-11T19:12:31.879+10:00	self.endheaders(body, encode_chunked=encode_chunked)

2023-04-11T19:12:31.879+10:00	File "/usr/local/lib/python3.10/http/client.py", line 1278, in endheaders

2023-04-11T19:12:31.879+10:00	self._send_output(message_body, encode_chunked=encode_chunked)

2023-04-11T19:12:31.879+10:00	File "/usr/local/lib/python3.10/site-packages/botocore/awsrequest.py", line 123, in _send_output

2023-04-11T19:12:31.879+10:00	self.send(msg)

2023-04-11T19:12:31.879+10:00	File "/usr/local/lib/python3.10/site-packages/botocore/awsrequest.py", line 218, in send

2023-04-11T19:12:31.879+10:00	return super().send(str)

2023-04-11T19:12:31.879+10:00	File "/usr/local/lib/python3.10/http/client.py", line 976, in send

2023-04-11T19:12:31.879+10:00	self.connect()
```
	
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

## Resources
- [AWS Samples Git Repo](https://github.com/orgs/aws-samples/repositories?language=&page=2&q=cloudformati&sort=&type=all)
- https://github.com/aws-samples/fargate-efs-cloudformation-deployment-example/blob/master/ecs_efs_template.yml
- https://github.com/ikatyang/emoji-cheat-sheet/blob/master/README.md
- [Private repository policy examples](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-policy-examples.html)
- https://docs.aws.amazon.com/cli/latest/reference/ecr/get-login-password.html
- --requires-compatibilities "FARGATE" (check the reference here: https://docs.aws.amazon.com/cli/latest/reference/ecs/register-task-definition.html)
- [Tutorial: Creating a cluster with a Fargate Linux task using the AWS CLI](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_AWSCLI_Fargate.html#ECS_AWSCLI_Fargate_register_task_definition)
- [CLI register task definition](https://docs.aws.amazon.com/cli/latest/reference/ecs/register-task-definition.html)
-  Amazon ECS Workshop > Introduction > ECS Overview > [Task Definitions](https://ecsworkshop.com/introduction/ecs_basics/task_definition/)
