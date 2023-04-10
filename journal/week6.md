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

### Create ECS Cluster
1. run these commands in CLI:
```
aws ecs create-cluster \
--cluster-name cruddur \
--service-connect-defaults namespace=cruddur
```
2. Check in AWS console that the cluster is created and new tasks are running
3. no need for security groups for now


	
## Create ECR repo and push image for backend-flask  
  https://www.youtube.com/watch?v=QIZx2NhdCMI&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=58
	
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
