# Week 6 — Deploying Containers

Contents:
1. [ECS Security Considerations](#ecs-security-considerations)
2. [Fargate Technical Questions](#fargate-technical-questions)
3. [Provision ECS Cluster](#provision-ecs-cluster)
4. [Create ECR repo and push image for backend-flask](#create-ecr-repo-and-push-image-for-backend-flask)
5. [Deploy Backend Flask app as a service to Fargate](#deploy-backend-flask-app-as-a-service-to-fargate)
6. [Create ECR repo and push image for fronted-react-js](#create-ecr-repo-and-push-image-for-fronted-react-js)
7. [Deploy Frontend React JS app as a service to Fargate](#deploy-frontend-react-js-app-as-a-service-to-fargate)
8. [Provision and configure Application Load Balancer along with target groups](#provision-and-configure-application-load-balancer-along-with-target-groups)
9. [Manage your domain useing Route53 via hosted zone](#manage-your-domain-useing-route53-via-hosted-zone)
10. [Create an SSL cerificate via ACM](#create-an-ss-cerificate-via-acm)
11. [Setup a record set for naked domain to point to frontend-react-js](#setup-a-record-set-for-naked-domain-to-point-to-frontend-react-js)
12. [Setup a record set for api subdomain to point to the backend-flask](#setup-a-record-set-for-api-subdomain-to-point-to-the-backend-flask)
13. [Configure CORS to only permit traffic from our domain](#configure-cors-to-only-permit-traffic-from-our-domain)
14. [Secure Flask by not running in debug mode](#secure-flask-by-not-running-in-debug-mode)
15. [Refactor bin directory to be top level](#refactor-bin-directory-to-be-top-level)
16. [Create Dockerfile specfically for production use case](#create-dockerfile-specfically-for-production-use-case)
17. [Implement Refresh Token for Amazon Cognito](#implement-refresh-token-for-amazon-cognito)
18. [Configure task defintions to contain x-ray and turn on Container Insights](#configure-task-defintions-to-contain-x-ray-and-turn-on-container-insights)
19. [Using ruby generate out env dot files for docker using erb templates](#using-ruby-generate-out-env-dot-files-for-docker-using-erb-templates)
20. [Change Docker Compose to explicitly use a user-defined network](#change-docker-compose-to-explicitly-use-a-user-defined-network)
21. [Resources](#resources)
	

## ECS Security Considerations
[Watched ECS Security by Ashish](https://www.youtube.com/watch?v=zz2FQAk1I28&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=57)
Best practice:
* scan on push
* enable tag immutability
* enable encryption with KMS
* access control following the least privilege principle
* use VPC endpoints
* granular access in security groups only for those who need access
* ensure compliance standard
* apply Organization SCPs for stricter access
* enable CloudTrail and Container insights
* enable Config rules (no GuardDuty for ECS?)
* only use safe images withought critical / high vulnerabilities
* do not store passwords in task definitions, use Secrets Manager instead

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


### Implement health check for backend container 
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

### Create CloudWatch Log Group 

1. got to AWS CloudWatch console
2. run these commands in CLI (or CloudShell):
```
aws logs create-log-group --log-group-name "/cruddur/fargate-cluster"
aws logs put-retention-policy --log-group-name "/cruddur/fargate-cluster" --retention-in-days 1
```
3. retention days set to 1 for the cost reason. The lowest it can be!
4. go back to the AWS CloudWatch console and check that '/cruddur/fargate-cluster' log group appeared

### Create ECS Cluster 
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

### Base Image Python :white_check_mark:
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

### Flask image :white_check_mark:

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
22. open port 4567 for this security group:
```bash
aws ec2 authorize-security-group-ingress \
  --group-id $CRUD_SERVICE_SG \
  --protocol tcp \
  --port 4567 \
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
--task b1391cf064974eb3b66ff3a33f13a399 \
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
40. create a new script 'connect-to-service 'in bin/ecs folder and make it executable with chmod u+x: 
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
42. I had to comment out xray lines in app.py
43. updated ecs security group to have inbound port 4567 instead of 80
44. fixed path for health-check CMD command in task definition
45. rebuilt backend-flask image, pushed it to ECR, ran command to create a new task revision in ECS
46. ran command to create an ECS service via CLI
47. the task appeared to be healthy! 
48. Commamd for listing tasks: ```aws ecs list-tasks --cluster cruddur```
49. go to EC2 -> security groups and select default security group
50. update inbound rules and add 5432 PostgreSQL port to be allowed for crud-srv-sg that we use for ECS
51. connect to container from Gitpod and when inside run this command: ```./bin/db/test```
52. expected reult from terminal shall show that connection was successful:
```
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ ./backend-flask/bin/ecs/connect-to-service a029820332714163b5249cc11cb6ba61TASK ID : a029820332714163b5249cc11cb6ba61
Container Name: backend-flask

The Session Manager plugin was installed successfully. Use the AWS CLI to start a session.


Starting session with SessionId: ecs-execute-command-07923b45efddc5250
root@ip-172-31-41-113:/backend-flask# ./bin/db/test
attempting connection
Connection successful!
root@ip-172-31-41-113:/backend-flask# 
```
53. go back to ECS task and copy its public IP. append it with :4567/api/activities/home
54. hooray, we are getting raw data from production RDS database: 
```json
[
  {
    "created_at": "2023-04-03T09:10:58.968124",
    "display_name": "Olley T",
    "expires_at": "2023-04-10T09:10:58.935268",
    "handle": "olleyt",
    "likes_count": 0,
    "message": "Crud button only works from home page",
    "replies_count": 0,
    "reply_to_activity_uuid": null,
    "reposts_count": 0,
    "uuid": "64596a14-552d-4ccb-9c10-3bce87998130"
  }
]
```
The endpoint is not secured and everyone cah hit it but we are one step closer with implementing Cruddur
55. go back to ECS console and delte the service
56. recreate it manually with 'Turn on Service Connect' option, map all fields except port to backend-flask and port to 4567
57. we will have a nice service url to connect to but for now let's delete this service
58. now we will restore deleted code for service connect in service-backend-flask.json
59. then create ECS service with CLI command: 
```
aws ecs create-service --cli-input-json file://aws/json/service-backend-flask.json
```
60. grab publick IP of the task and check the health check still returns success
61. create ALB in AWS Console (GUI), service connect is able to work with ALB
    * name: cruddur-alb
    * select all subnets for the default VPC
    * create new security group: cruddur-alb-sg and add inbound rules for ports 80 and 443 for all IPv4 addresses (temporarily can add your own IP address)
    * deviation: set outbound rule to crud-srv-sg security group

62. go back to crud-srv-sg security group and update inbound rule on port 4567 to allow only the ALB security group
63. create a new target group
    * target type: IP addresses
    * name: cruddur-backend-flask-tg
    * port: 4567
    * health check protocol: HTTP
    * health check path: /api/health-check
    * threshold: 3
    * click next
    * create without associating targets

64. go back to the page where we create the load balancer
65. in 'Listeners and routing', choose port 4567 and choose the just created target group
66. add listener for the frontend and add a new target group:
    * target type: IP addresses
    * name: cruddur-frontend-react-js-tg
    * port: 3000
    * health check protocol: HTTP
    * health check path: /
    * threshold: 3
    * click next
    * create without associating targets
67. review and create the load-balancer
68. go back to service-backend-flask.json to add load balancer
69. create ECS service via CLI again
```
aws ecs create-service --cli-input-json file://aws/json/service-backend-flask.json
```
70. temporarily add port 4567 and 3000 from anywhere inbound rule on the ALB security group
71. now errors on ALB listeners shall disappear
72. check that ECS task is healthy and related target group is healthy
73. copy ALB DNS name and post it to a browser and append it with :4567/api/health-check
74. web page shall return 
```
{
  "success": true
}
```
75. go to S3 console
76. create a public S3 bucket in the same region as CloudWatch for this project
77. turn on access logs for the ALB on tab Attributes


## Create ECR repo and push image for fronted-react-js	
[stream link](https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59)
78. create file frontend-react-js.json in task-definitions folder (GitPod) - get one from Andrews week6-fargate branch
79. create Dockerfile.prod for frontend-react-js container. We will be using multi-stage build for frontend container
80. create file nginx.conf file in the frontend-react-js folder
81. cd frontend-react-js in terminal
82. run ```npm run build``` -> ignore warnings (for now)
83. add build folder into .gitignore
84. build frontend image:
```
docker build \
--build-arg REACT_APP_BACKEND_URL="https://4567-$GITPOD_WORKSPACE_ID.$GITPOD_WORKSPACE_CLUSTER_HOST" \
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="us-east-1_vBKMcxpJ9" \
--build-arg REACT_APP_CLIENT_ID="7tp9c32crfu6hk1rdk43qiah33" \
-t frontend-react-js \
-f Dockerfile.prod \
.
```
85. create repo:
```
aws ecr create-repository \
  --repository-name frontend-react-js \
  --image-tag-mutability MUTABLE
```
86. set URL for front-end:
```
export ECR_FRONTEND_REACT_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/frontend-react-js"
echo $ECR_FRONTEND_REACT_URL
```
87. login to ECR:
```
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
```
88. tag image:
```
docker tag frontend-react-js:latest $ECR_FRONTEND_REACT_URL:latest
```
89. push image:
```
docker push $ECR_FRONTEND_REACT_URL:latest
```
90. run the new frontend image locally:
```
docker run --rm -p 3000:3000 -it frontend-react-js 
```
91. add file service-frontend-react-js.json (see commit history). Not sure if security group shall be crud-srv-sg
92. in order to avoid CORS issues, we need to rebuild the image with the load balancer DNS name, not local GitPod URL
```
docker build \
--build-arg REACT_APP_BACKEND_URL="http://cruddur-alb-1822031801.us-east-1.elb.amazonaws.com:4567" \
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="us-east-1_vBKMcxpJ9" \
--build-arg REACT_APP_CLIENT_ID="7tp9c32crfu6hk1rdk43qiah33" \
-t frontend-react-js \
-f Dockerfile.prod \
.
```
93. tag and push the image to ECR as done on steps 87-89

  
## Deploy Frontend React JS app as a service to Fargate
[stream link](https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59)
94. cd ..
95. create front-end task definition:
```
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/frontend-react-js.json
```
96. create a front-end service:
```
aws ecs create-service --cli-input-json file://aws/json/service-frontend-react-js.json
```
97. however the service is failing. Andrew built a local image without ALB. Then he tried to inspect this container.
98. NOT REQUIRED: go to the frontend target group and override port for health check to 3000 - no need for that
99. add port 3000 for inbound rule for crud-srv-sg security group allowing ALB security group to access it on port 3000
100. create ECS frontend service again via CLI
101. now we see both services running healthy: 
102. ![ecs_2_services](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/374f1d75359de55034a3bbf3e4d482b5c34792e8/_docs/assets/ecs_2_service_running.png)
103. go to the load balancer and copy its DNS name
104. copy the DNS name to Chrome and append with :3000
105. woohoo! Cruddur web site is now loaded with data!
![cruddur_behind_alb](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/374f1d75359de55034a3bbf3e4d482b5c34792e8/_docs/assets/cruddur_fargate.png)
105. tear down ALB and ECS tasks for cost savings. stop RDS

## Provision and configure Application Load Balancer along with target groups	
[stream link](https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59)
was done in previous section from step 61
	
## Manage your domain useing Route53 via hosted zone	
[stream link](https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59)
My domain was bought via Amazon Route 53 service, and AWS automatically created a hosted zone with NS and SOA records
	
## Create an SSL cerificate via ACM	
[stream link](https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59)

1. go to AWS console and navigate to Certificate manager
2. request public certificate
3. enter fully qualified domain name
4. add ```*.<your fully qualified domain name>``` as another domain for the certificate
5. choose DNS validation
6. click Request	
7. the certificate will be in pending validation state
8. click on the created certificate and on Domains frame click 'Create records in Route 53'
9. in the new window, click 'Create Records' button
10. go back to Route 53 , and see that CNAME record was added to the hosted zone
11. wait a little while and see that records have 'Success' status on the certificate
12. we probably shall enable DNSSSEC at some point
13. go back to our load balancer, and create a new listener on port 80 and add redirect it to 443
14. add a new listener for port 443 and a forward rule to frontend target group. Choose default SSL/TLS certificate
15. delete listeners for ports 4567 and 3000
16. choose listener for port 443 and click on Actions and select Manage Rules
17. add a rule under host header and put value ```api.<yourdomain>``` in field 'is' and forward traffic to backend target group
	
## Setup a record set for naked domain to point to frontend-react-js 
[stream link](https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59)
1. go to Route 53, choose our hosted zone
2. add A record for naked domain routing to ALB
	
	
## Setup a record set for api subdomain to point to the backend-flask 
https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59
1. go to Route 53, choose our hosted zone
2. add A record for api sub domain routing to ALB
3. run curl command
```
curl api.architectingonaws.link/api/health-check

```
or post in the browser: https://api.architectingonaws.link/api/health-check
returns:
```
{
  "success": true
}
```
	
	
## Configure CORS to only permit traffic from our domain 	
[stream link](https://www.youtube.com/watch?v=HHmpZ5hqh1I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=59)

1. go to ```backend-flask.json``` task definition and change these two lines to specifc domains:
```{"name": "FRONTEND_URL", "value": "https://architectingonaws.link"},```
```{"name": "BACKEND_URL", "value": "https://api.architectingonaws.link"}```
	
2. run command to create a new revision for this task definition:
```
aws ecs register-task-definition --cli-input-json file://aws/task-definitions/backend-flask.json
```
3. login to ECR
4. build front-end image and change ```REACT_APP_BACKEND_URL="https://api.architectingonaws.link"```
```
docker build \
--build-arg REACT_APP_BACKEND_URL="https://api.architectingonaws.link" \
--build-arg REACT_APP_AWS_PROJECT_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_COGNITO_REGION="$AWS_DEFAULT_REGION" \
--build-arg REACT_APP_AWS_USER_POOLS_ID="us-east-1_vBKMcxpJ9" \
--build-arg REACT_APP_CLIENT_ID="7tp9c32crfu6hk1rdk43qiah33" \
-t frontend-react-js \
-f Dockerfile.prod \
.	
```
5. tag and push this image
6. update backend ECS service with the latest task definition revision (AWS Console)	
7. force update existing frontend ECS service
8. check that both targets groups are healthy
9. check backend health-check in the browser: ```https://api.architectingonaws.link/api/health-check```	
10. check website: ```https://architectingonaws.link```
11. we can see CORS errors in Network tab of developer tools in Chrome
12. connect to ECS service from the terminal in Gitpod, type env to check environment variables
13. Andrew added protocol ```https://``` in FRONTEND_URL and BACKEND_URL in backend-flask.json task definition as attempt to rectify the CORS issue. He updated task definition and updated the back-end service. It worked for him so I updated step 1 of this section.
14. sign in into Cruddur and try to create a Crud
15. go to messages and create a new message appending ```/messages/new/@handleofuser```. Andrew hit the 500 error but it worked for me.	
	
## Secure Flask by not running in debug mode 	
[stream link](https://www.youtube.com/watch?v=9OQZSBKzIgs&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=60)
1. go to EC2 in AWS Console, navigate to ALB security group
2. delete inbound rules for ports 3000, 4567
3. change Source to My IP for both 80 and 443 ports
4. go to GitPod and create a Dockerfile.prod for backend container
5. Create a new folder ecr in bin directory and create a new script ```login``` inside of it
6. ```chmod u+x ./ecr/login```
7. login to ECR: ```./ecr/login``` from backend-flask/bin directory```
8. buid new image: ```docker build -f Dockerfile.prod -t backend-flask-prod .```
9. Andrew tested new image locally with docker run command which he put as a script named backend-flask-prod in a new folder ```/bin/docker```:
```
docker run --rm \
-p 4567:4567 \
--env AWS_ENDPOINT_URL="http://dynamodb-local:8000" \
#--env CONNECTION_URL="postgresql://postgres:password@db:5432/cruddur" \
--env CONNECTION_URL="${PROD_CONNECTION_URL}"
--env FRONTEND_URL="https://3000-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}" \
--env BACKEND_URL="https://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}" \
--env OTEL_SERVICE_NAME='backend-flask' \
--env OTEL_EXPORTER_OTLP_ENDPOINT="https://api.honeycomb.io" \
--env OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=${HONEYCOMB_API_KEY}" \
--env AWS_XRAY_URL="*4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}*" \
--env AWS_XRAY_DAEMON_ADDRESS="xray-daemon:2000" \
--env AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
--env AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
--env AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
--env ROLLBAR_ACCESS_TOKEN="${ROLLBAR_ACCESS_TOKEN}" \
--env AWS_COGNITO_USER_POOL_ID="${AWS_COGNITO_USER_POOL_ID}" \
--env AWS_COGNITO_USER_POOL_CLIENT_ID="5b6ro31g97urk767adrbrdj1g5" \   
-it backend-flask-prod
```
Note: links to local databases need a revision on my side
10. create subfolders run and build inside docker folder. put backend-flask-prod script into build folder. Create a new script for command in step 8 and call it backend-flask-prod. Also create a script in build folder called frontend-react-js
11. run container from GitPod : ```./backend-flask-prod```
12. temporarily cause an error in app.py in health-check path with calling non-existent function:
```
@app.route('/api/health-check')
def health_check():
  hello()
  return {'success': True}, 200
``` 
13. run docker-compose up and see if we see error in a debugging mode and if we can tamper with it
14. open Cruddur app from backend in the browser and append url with ```/api/health-check```
15. we get error ```NameError: name 'hello' is not defined``` as expected, however we don't want to show error stack trace in browser
16. go to backend Dockerfile non-prod and change debugging flag to ```--no-debug```, run docker-compose up
17. evidence that ```/api/health-check``` now throws ```Internal Server Error```. That proves that we secured flask app so no-one can tamper with it in debug mode.
18. run docker-compose down and fix app.py
19. continue with [part 2 of securing flask](https://www.youtube.com/watch?v=eaeEbeEVNMk)
20. run ```./bin/docker/build/backend-flask-prod```
21. create folder push inside docker folder and create scripts backend-flask-prod and frontend-react-js-prod scripts. Add tag and push commands for each and make these scripts executable, add path variables for that too. (See stream at 6:58 point)
22. create backend-flask/bin/ecs/force-deploy-backend-flask with updating ecs task definition for backend-flask. (Video stream point is at at 15th min). Andrew noted that last describe command is not that useful because we want to continiuosly monitor created services.
	
## Refactor bin directory to be top level	
[stream link](https://www.youtube.com/watch?v=HyJOjBjieb4&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=62)

23. create 'bin' directory at the top level of the workspace
24. move /backend-flask/bin/rds into /bin/rds and rename script rds-update-sg-rule to update-sg-rule. Update gitpod.yml accordingly.
25. move all directories from /backend-flask/bin/ to /bin except /flask because we need to keep health-check in backend-flask folder
26. refactor db utility scripts that connectingto RDS / local PostgreSQL container to use absolute path
27. refactor docker biold scripts for backend and front end to use absolute path. (Stream point: 31:20)
28. further refctor db setup, update_cognito_user_ids, seed and seed.sql scripts following the video stream. Note: I don't use mock data because those users are not in my cognito pool and I am not listing my users in public repository for security reasons
29. refactor bin directory and have explicit folders for frontend and backend with build, run, deploy, connect scripts for easier use
30. delete existing ECS servies in AWS console
31. login to ECR from the Gitpod terminal then rebuild and push frontend and backend services
32. using new scripts, create ECS services
33. check ECS task health, ALB target health, login to Cruddur and try to create new messages

## Create Dockerfile specfically for production use case
[stream link](https://www.youtube.com/watch?v=G_8_xtS2MsY&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=64)
Those files were added during implementing front-end image and securing Flask application homework tasks. 
[backend Dockerfile.prod](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/d8fe2966aa059bd692c4a0d456827f117c5926e7/backend-flask/Dockerfile.prod)
[frontend Dockerfile.prod](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/d8fe2966aa059bd692c4a0d456827f117c5926e7/frontend-react-js/Dockerfile.prod)

## Implement Refresh Token for Amazon Cognito	
[stream link](https://www.youtube.com/watch?v=LNLP2dxa5EQ&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=63)

*Problem:* CheckAuth.js is not attempting to refresh token

*Solution*: Andrew was looking how to do that at Amplify Dev Center, react-native-sample example but it was not giving a Cognito example.
We need to get Auth.currentSession() to get the refreshed token from Amplify.
We will wrap each of our API calls in getting refreshed token from new function getAccessToken() defined in CheckAuth.js.
Changed code units:
* CheckAuth.js
* HomeFeed.js
* MessageForm.js
* MessageGroupNewPage.js
* MessageGroupPage.js
* MessageGroupsPage.js

*Testing:*
* spin up GitPod
* run /bun/ecr/login script
* run docker-compose up
* run db scripts: db/setup, /ddb/schema-load and seed data to local databases (PostgreSQL and DynamoDB). Note: I still need to add my own users to seed script with handles and emails as I set up in Cognito user pool
* login to Cruddur and do overall test and create some messages. Perhaps implementing Cypress e2e tests could be a good idea
	
## Configure task defintions to contain x-ray and turn on Container Insights
[stream link](https://www.youtube.com/watch?v=G_8_xtS2MsY&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=64)

### X-Ray containers
1. add these lines into aws/task-definitions/backend-flask.json:
```json
    {
      "name": "xray",
      "image": "public.ecr.aws/xray/aws-xray-daemon" ,
      "essential": true,
      "user": "1337",
      "portMappings": [
        {
          "name": "xray",
          "containerPort": 2000,
          "protocol": "udp"
        }
      ]
    },
```
2. create new scripts called 'register' for backend and frontend to register updated task definitions
3. workflow when the backend code changes
    * ./bin/ecr/login
    * ./bin/backend/register - when task definition got updated
    * ./bin/backend/build
    * ./bin/backend/push
    * ./bin/backend/deploy
    * ./bin/backend/run - for local debugging
4. login to AWS Console and navigate to ECS, services, go to backend task and see xray container is running    
5. note: I have previously commented out X-Ray code in app.py and user_activities.py as my docker images were not building
6.  after implementing custom network and generating environment variables (follow 2 sections below first), add hostname in docker-compose file:
```bash
  xray-daemon:
    hostname: xray-daemon
    image: "amazon/aws-xray-daemon"
    environment:
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
```
7. even after implementing environment files and streamlining docker-compose file, we could not get health check on Xray working. Andrew tried netstat suggestion from StackOverflow but unfortunately it did not work out, so we left Xray health-check not implemented for now. He removed health check from backend-flask.json task definition and re-registered the task.
8. then run deploy of the backend task, login to AWS ECS console and see that backend is now healthy and we can access the app
9. add same xray container definition to frontend ECS task definition json, run register and deploy scripts for it

### Turning on Container Insights
1. login to AWS Console -> ECS -> select cruddur cluster
2. go to monitor tab and turn on container insights
3. login to Cruddur, check and post messages
4. go to CloudWatch and select 'Container insights' on left hand pane. Now we shall see container insights logs 

## Using ruby generate out env dot files for docker using erb templates
[stream link](https://www.youtube.com/watch?v=G_8_xtS2MsY&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=64)

1. Initially Andrew created env files at the root of the workspace with copying env variables as they were defined in docker compose file.
2. However, docker run scripts were not parsing variables correctly.
3. Note: Andrew used CONNECTION_URL set to local PostgreSQL whereas I set CONNECTION_URL = PROD_CONNECTION_URL since I have not used the mock data in order to save on GitPod credits and hence didn'y run local psql container.
4. we observed that ```--env``` in docker run scripts did not resolve environment variables referencing such as ```${GITPOD}``` but left this text as is.
5. Hence, Andrew decided to create scripts that will transform environment variables reference and create ```.env``` files by creating Ruby scripts named ```generate-env``` in  ```bin/backend``` folder:
```bash
#!/usr/bin/env ruby

require 'erb'

template = File.read 'erb/backend-flask.env.erb'
content = ERB.new(template).result(binding)
filename = "backend-flask.env"
File.write(filename, content)
```
6. and for ```bin/frontend``` folder:
```bash
#!/usr/bin/env ruby

require 'erb'

template = File.read 'erb/frontend-react-js.env.erb'
content = ERB.new(template).result(binding)
filename = "frontend-react-js.env"
File.write(filename, content)
```
7. make both of the scripts executable with ```chmod u+x command```
8. then we had to create erb templates that were placed in erb folder which was created at the root of the workspace: ```backend-flask.env.erb``` and ```frontend-react-js.env.erb```
9. add the generated ```*.env``` files to ```.gitignore``` so passwords and secrets are not published in GitHub.
10. change ```.gitpod.yaml``` *init* tasks to *before* tasks and add generating env files for backend:
``` source "$THEIA_WORKSPACE_ROOT/bin/backend/generate-env" ```
and for frontend:
```
source "$THEIA_WORKSPACE_ROOT/bin/frontend/generate-env"
```
11. edit docker run files to implement env file referencing:
12. frontend run script:
```bash
#! /usr/bin/bash

ABS_PATH=$(readlink -f "$0")
BACKEND_PATH=$(dirname $ABS_PATH)
BIN_PATH=$(dirname $BACKEND_PATH)
PROJECT_PATH=$(dirname $BIN_PATH)
ENVFILE_PATH="$PROJECT_PATH/frontend-react-js.env"

docker run --rm \
  --env-file $ENVFILE_PATH \
  --network cruddur-net \
  --publish 4567:4567 \
  -it frontend-react-js-prod
```
13. backend run script:
```bash
#! /usr/bin/bash

# I am using production RDS and DynamoDB, local databases are empty
#--env AWS_ENDPOINT_URL="http://dynamodb-local:8000" \

ABS_PATH=$(readlink -f "$0")
BACKEND_PATH=$(dirname $ABS_PATH)
BIN_PATH=$(dirname $BACKEND_PATH)
PROJECT_PATH=$(dirname $BIN_PATH)
ENVFILE_PATH="$PROJECT_PATH/backend-flask.env"

docker run --rm \
  --env-file $ENVFILE_PATH \
  --network cruddur-net \
  --publish 4567:4567 \
  -it backend-flask-prod
```
14. run generate-env scripts
15. specify env files in docker-compose.yml:
```
....
  backend-flask:
    env_file:
      - backend-flask.env
....      
  frontend-react-js:
    env_file:
      - frontend-react-js.env
....
```
16. create busybox script in ./bin directory, make it executable:
```
#! /usr/bin/bash

docker run --rm \
  --network cruddur-net \
  --publish 4567:4567 \
  -it busybox
```
17. run the script and also add /bin/bash to get into the container
18. Andrew tried to ping google and it was succesful, but then he figured out that environment file for docker run command shall not have quotation marks for surrounding environment variables values
19. remove quotation marks in erb templates
20. run docker-compose up and it shall work

## Change Docker Compose to explicitly use a user-defined network
[stream link](https://www.youtube.com/watch?v=G_8_xtS2MsY&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=64)

1. Looking at the Docker docs, it seems that we need to use [network in bridge mode](https://docs.docker.com/network/bridge/).
2. We can see list of networks for our project by typing this command in GitPod terminal:
```docker network list```
3. Andrew used this sequence to see which network our container are connected to:
```bash
docker-compose up
bin/db/setup
bin/backend/run
docker network list
```
4. We need to create our own network ```cruddur-net``` in docker-compose.yml so container services can communicate. Make sure all services connetced to this network:
```
...
    build: ./backend-flask
    ports:
      - "4567:4567"
    volumes:
      - ./backend-flask:/backend-flask
    networks:
      - cruddur-net
 ...
 build: ./frontend-react-js
    ports:
      - "3000:3000"
    networks:
      - cruddur-net
 ...
 container_name: dynamodb-local
    ports:
      - "8000:8000"
    networks:
      - cruddur-net
 ...
 ports:
      - '5432:5432'
    networks:
      - cruddur-net
 ...
       - "xray -o -b xray-daemon:2000"
    ports:
      - 2000:2000/udp
    networks:
      - cruddur-net
# the name flag is a hack to change the default prepend folder
# name when outputting the image names
networks: 
  cruddur-net:
    driver: bridge
    name: cruddur-net
```    
	

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
- [How to remove multiple docker images with the same imageID?](https://stackoverflow.com/questions/32944391/how-to-remove-multiple-docker-images-with-the-same-imageid)
- [How to remove docker images based on name?](https://stackoverflow.com/questions/40084044/how-to-remove-docker-images-based-on-name)
