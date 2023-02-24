# Week 1 — App Containerization


## Mandatory Tasks - Completed

### Watched videos required for self-improvement
These videos are excellent source how to be a better Cloud engineer and a team member in general:
* Watched [How to Ask for Technical Help](https://www.youtube.com/watch?v=tDPqmwKMP7Y&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=29)
* Watched [Grading Homework Summaries](https://www.youtube.com/watch?v=FKAScachFgk&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=25)
    * *Notes*:
    * the summary shall be plain text
    * shall not go into details
    * shall not include links; reserve them for the journal
    * being concise might be hard bit it respects everyone's time and it is a valuable skill for any workplace

### Commiting Code
Watched [Remember to Commit Your Code](https://www.youtube.com/watch?v=b-idMgFFcpg&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=23)

#### Notes:
* preferably use git commands in terminal rather than VSCode GUI in GitPod. 
    * It helps to understand better what is git status is, what are untracked / staged changes are and allow to see git's feedback on ```git push``` command in case the local main branch diverted from the remote origin in GitHub. 
* make small frequent changes
* make commits atomic - it will save time on troubleshooting and reverting problematic code
* do fetch before push if working on the same branch in different code spaces such as GitHub for journaling and GitPod for the code changes
   * alternatively work on journal in a separate branch but don't forget to merge into main before submitting week's work   

### Spending Considerations
Watcked Chirag's Week 1 - [Spending Considerations](https://www.youtube.com/watch?v=OAMHu1NiYoI&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=24)

#### Notes: 
* remember to stop a workspace when not used to keep under the free tier
* check billing page for remaining credits regularly
* delete unused workspaces to reduce clatter and cost

### Container Security Considerations
Watched Ashish's Week 1 - [Container Security Considerations](https://www.youtube.com/watch?v=OjZz4D0B-cA&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=25)

#### Notes: 
* running Snyk on Cruddur repository identified 6 critical vulnerabilities related mostly to outdated openssl and Node. More on that in 'Stretch Challenges' section. I have asked Ashish and Andrew if we were to attempt to fix these vulnerabilities. 
* try to run Snyk on container images as a stretch challenge
* try Inspector when we progress pushing Docker impages to ECR


### Completed Technical Tasks - Code Changes Committed
These tasks were completed without issues following along the videos and committing code changes from GitPod.
The commits can be found in the git history for the main branch.

* Watched Week 1 - [Live Streamed Video](https://www.youtube.com/watch?v=zJnNe5Nv4tE&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=22)
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

## Mandatory task challenges I faced and how I overcame them

### GitPod not persisting AWS CLI installations between start stops
   
#### Workaround
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
#### The proper solution with prebuilds and custom .gitpod.Dockerfile
This was quite a stretch challenge to comprehend why AWS CLI was not available after a GitPod environment restarted.
I followed [article posted by Jason Paul](https://www.linuxtek.ca/2023/02/21/diving-deeper-gitpod-cloud-development-environment/) to understand what are GitPod tasks, what is before block and what is init block and how they are different from each other.
   
The following code was copied to .gitpod.yml from the Jason Paul blog to offload libraries installations during prebuild:   
```bash
# copied from GitPodify guide: https://www.gitpod.io/guides/gitpodify#accelerating-startup-with-prebuilt-workspaces
github:
  prebuilds:
    # enable for the master/default branch (defaults to true)
    master: true
    # enable for all branches in this repo (defaults to false)
    branches: false
    # enable for pull requests coming from this repo (defaults to true)
    pullRequests: true
    # add a check to pull requests (defaults to true)
    addCheck: true
    # add a "Review in Gitpod" button as a comment to pull requests (defaults to false)
    addComment: false
```

In addition, AWS CLI and PostgreSQL client installation were moved to the .gitpod.Dockerfile as GitPod runs on a Docker container but customisation is required to persist tools installed outside of /workspace folder. The [Gitpodify](https://www.gitpod.io/guides/gitpodify) guide talks about this in more details and also provides examples how to write commands for the .gitpod.Dockerfile.
   
*Notes:* 
   * use '&&' for running subsequent commands on different lines. I guess it has to do with Docker RUN command syntax. Will need to investigate later.
   * use '\' for line break for longer commands
   * watch Andrew's full Gitpod course [here](https://www.youtube.com/watch?v=XcjqapXfrhk) to address GitPod knowledge gaps
   * credits: looked up and copied most of the gitpod.Dockerfile from Jason Paul resources and messages on Discord while I was figuring out Docker commands and Gitpod but then created my own .gitpod.dockerfile from scratch to avoid plagiarism.
   
At this point .gitpod.dockerfile shall look like this:
```yml
FROM gitpod/workspace-full:latest

# installs AWS CLI on a local GitPod env (not container)
# the code copied from Jason's Paul blog: https://www.linuxtek.ca/2023/02/21/diving-deeper-gitpod-cloud-development-environment/
RUN cd /workspace \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && sudo /workspace/aws/install
    
# installs PostreSQL on a local GitPod env (not container)
# command is adopted to Docker RUN command from Andrew's Brown week1.md instructions
RUN curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc|sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list \
    && sudo apt update \
    && sudo apt install -y postgresql-client-13 libpq-dev
```   
Don't forget to add these lines at the top of .gitpod.yml file:
```yml
image:
  file: .gitpod.dockerfile   
```   
   
### Installing Python libraries and npm on init stage
In order to have a new fully functioning GitPod environment with everything required being installed in workspace, Python libraries need to be installed in the backend-flask folder and npm needs to be installed in the frontend-react-js folder during the init task as specified in .gitpod.yml:
```yml
tasks:
  - name: Customising Workspace
    env:
      AWS_CLI_AUTO_PROMPT: on-partial
    init: |
      # install Python libraries for Flask backend app on local GitPod environment
      cd $THEIA_WORKSPACE_ROOT/backend-flask
      pip3 install -r requirements.txt
      # install npm libraries for frontend on local GitPod environment
      cd $THEIA_WORKSPACE_ROOT/frontend-react-js
      npm i
      cd $THEIA_WORKSPACE_ROOT   
```  
Expected result: GitPod will persist Python and Node libraries as they were installed inside /workspace folder between environment restarts. 
Actual result: matches expected result.   
   
   
### GitPod did not have Docker extension preinstalled

This was rectified in .gitpod.yml by adding ms-azuretools.vscode-docker into extensions like so:
```yml
   vscode:
     extensions:
       - 42Crunch.vscode-openapi
       - ms-azuretools.vscode-docker
       - cweijan.vscode-postgresql-client2
```  
#### Instruction how to add extensions to .gitpod.yml:
1. go to VSCode marketplace
2. find the missing extension
3. click on the cog icon and select 'add to .gitpod.yaml'
4. commit .gitpod.yaml to the repository

### Docker compose file was in incorrect folder

When I ran compose up first time from the left navigation pane, Docker did not produce working containers and both containers were in red status. 
* _Trobleshooting steps:_
    * I looked into the logs and the error was saying that FLASK_APP variable is not set and some files are not found. 

* _Solution:_
    * The problem was that I created docker-compose not on the root but inside the the front-end folder when clicked adding file on the left side pane! Sometimes I love bash commands better than point & click approach. It was such a baffling and silly error to create file in a wrong place. 

* _Status:_
    * It's all working now. 

## Stretch Challenges      

### 1. Cruddur AWS user access is following least priviledge principle:
   * Specific policies were added directly to a user. 
   * This user does not have console access, but Admin user does for managing IAM users, roles, and policies
   * the DynamoDB policy was described above
### 2. Ran Snyk scan on my Cruddur repo:
   * Snyk identified 6 critical vulnerabilities recommending to upgrade openssl and npm
   * There are more than 400 unfixiable low priority vulnerabilities as well
   * [Snyk screenshot](../_docs/assets/Snyk_report_cruddur.png)
### 3. Homework Challenges for week1
#### 3.1 Run the dockerfile CMD as an external script
This challenge will solve how to run the command in CMD statement for backend.   
   Steps:
   1. Instead of 
   ``` CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]``` create a shell script run_flask_app.sh to run the command that will run flask application as follows:

```bash
#!/bin/bash
python3 -m flask run --host=0.0.0.0 --port=4567
```
   2. commit the file to the repository
   3. make the shell script executable:
   ```bash
   chmod +x run_flask_app.sh.sh
   ```
   4. change CMD command in /backend-flask/Dockerfile from ```CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]``` to ```CMD [ "./run_flask_app.sh"]```
   5. commit code changes to the repository
   6. run docker compose up
   7. open exposed ports on the GitPod ports terminal tab
   8. test the app from frontend link

#### 3.2 Push and tag an image to DockerHub
   1. The general command to build an image with a tag for DockeHub:
   ```docker build -t <your-dockerhub-username>/<your-image-name>:<version-number> ```
   
   For this challenge, backend-flask container image will be tagged and pushed to Docker Hub like so:
   ```
   docker build -t  olleyt/backend-flask:1 ./backend-flask

   ```
   2. login to Docker from GitPod instance with ``` docker login``` command
   3. push the image like so:
   ```bash
   docker push  olleyt/backend-flask:1
   ```
   4. Expected result shall look similar to the snipped below:
   ```bash
   gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ docker push  olleyt/backend-flask:1
   The push refers to repository [docker.io/olleyt/backend-flask]
   42c37f51f3a3: Pushed 
   0634a93e7070: Pushed 
   f2ce57a5fa3d: Pushed 
   c7c5c5260b32: Pushed 
   223e3b83550e: Mounted from library/python 
   53b2529dfca9: Mounted from library/python 
   5be8f6899d42: Mounted from library/python 
   8d60832b730a: Mounted from library/python 
   63b3cf45ece8: Mounted from library/python 
   1: digest: sha256:d124ef065b7c6217aef1dba412492382437e6e68aa287cebedd179a6d34e91e4 size: 2203
   ```
   5. Sanity check: login into Docker Hub on the desktop and check that the image was uploaded like on [this screenshot](../_docs/assets/DockerDesktop-cruddur-backend-flask.png)

####   
1. As Docker was already installed on my local machine prior the bootcamp while doing Adrian's Cantrill Docker course, we can proceed to the next step. We will use the same container pushed into Docker hub that was built for tag/push challenge ```  olleyt/backend-flask:1 ```
2. Firstly, a container needs to be pulled to local machine. This can be achieved by running this command in the terminal:
   ``` docker pull olleyt/backend-flask:1 ```
   Expected result (see that SHA is matching to the pushed image):
   ```bash
   ~ $ docker pull olleyt/backend-flask:1
   1: Pulling from olleyt/backend-flask
   29cd48154c03: Pull complete 
   2c59e55cfd71: Pull complete 
   3b4b58298de0: Pull complete 
   6239e464c1ab: Pull complete 
   047dd5665bb1: Pull complete 
   e91f6c455615: Pull complete 
   805848c55aec: Pull complete 
   7e9a866e7ad6: Pull complete 
   8add47a00289: Pull complete 
   Digest: sha256:d124ef065b7c6217aef1dba412492382437e6e68aa287cebedd179a6d34e91e4
   Status: Downloaded newer image for olleyt/backend-flask:1
   docker.io/olleyt/backend-flask:1
   ```
 3. next run the Docker container with following command: 
   ```docker run --rm -p 4567:4567 -it -e FRONTEND_URL='*' -e BACKEND_URL='*' olleyt/backend-flask:1```
   expected result: the container is running and stdout also provides a link to access the running Flask app. don't forget to append with /api/activities/home:
   ```bash
   ~ $ docker run --rm -p 4567:4567 -it -e FRONTEND_URL='*' -e BACKEND_URL='*' olleyt/backend-flask:1
      WARNING: The requested image's platform (linux/amd64) does not match the detected host platform (linux/arm64/v8) and no specific platform was requested
      'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
      'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
      'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
       * Debug mode: on
      WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
       * Running on all addresses (0.0.0.0)
       * Running on http://127.0.0.1:4567
       * Running on http://172.17.0.2:4567
      Press CTRL+C to quit
       * Restarting with stat
      'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
      'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
      'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
       * Debugger is active!
       * Debugger PIN: 893-092-020
      172.17.0.1 - - [24/Feb/2023 05:57:28] "GET / HTTP/1.1" 404 -
      172.17.0.1 - - [24/Feb/2023 05:57:28] "GET /favicon.ico HTTP/1.1" 404 -
      172.17.0.1 - - [24/Feb/2023 05:57:39] "GET /activities/home HTTP/1.1" 404 -
      172.17.0.1 - - [24/Feb/2023 05:58:38] "GET /api/activities/home HTTP/1.1" 200 -
   ```
  4.  the container is running and stdout also provides a link to access the running Flask app. don't forget to append with /api/activities/home in the browser:
   ```http://127.0.0.1:4567/api/activities/home```
   expected result: JSON response will appear like so:
   ```json
   [
  {
    "created_at": "2023-02-22T05:58:38.636165+00:00",
    "expires_at": "2023-03-01T05:58:38.636165+00:00",
    "handle": "Andrew Brown",
    "likes_count": 5,
    "message": "Cloud is fun!",
    "replies": [
      {
        "created_at": "2023-02-22T05:58:38.636165+00:00",
        "handle": "Worf",
        "likes_count": 0,
        "message": "This post has no honor!",
        "replies_count": 0,
        "reply_to_activity_uuid": "68f126b0-1ceb-4a33-88be-d90fa7109eee",
        "reposts_count": 0,
        "uuid": "26e12864-1c26-5c3a-9658-97a10f8fea67"
      }
    ],
    "replies_count": 1,
    "reposts_count": 0,
    "uuid": "68f126b0-1ceb-4a33-88be-d90fa7109eee"
  },
  {
    "created_at": "2023-02-17T05:58:38.636165+00:00",
    "expires_at": "2023-03-05T05:58:38.636165+00:00",
    "handle": "Worf",
    "likes": 0,
    "message": "I am out of prune juice",
    "replies": [],
    "uuid": "66e12864-8c26-4c3a-9658-95a10f8fea67"
  },
  {
    "created_at": "2023-02-24T04:58:38.636165+00:00",
    "expires_at": "2023-02-24T17:58:38.636165+00:00",
    "handle": "Garek",
    "likes": 0,
    "message": "My dear doctor, I am just simple tailor",
    "replies": [],
    "uuid": "248959df-3079-4947-b847-9e0892d1bab4"
  }
]
   ```
   
## This week I learned:
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
   
However, learning time is required to complete these challenges for this week:
* Use multi-stage building for a Dockerfile build
* Implement a healthcheck in the V3 Docker compose file
* Research best practices of Dockerfiles and attempt to implement it in your Dockerfile
* Launch an EC2 instance that has docker installed, and pull a container to demonstrate you can run your own docker processes
      
On the bright side, I was able to finish all the mandatory assignments without issues and these homework challenges:
* Run the dockerfile CMD as an external script
* Push and tag a image to DockerHub (they have a free tier)
* Learn how to install Docker on your localmachine and get the same containers running outside of Gitpod / Codespaces

### GitPod Custom Image
This week I learned from [article posted by Jason Paul](https://www.linuxtek.ca/2023/02/21/diving-deeper-gitpod-cloud-development-environment/) that GitPod persists only /workspace and managing dependencies and longer running installations shall be done via customizing docker file for GitPod: .gitpod.Dockerfile

That helped to resolved missing AWS CLI after each stop / start of my GitPod environment.

### Open API
This week was a great opportunity to learn how to design and document REST APIs with OpenAPI specification (former Swagger).
The OpenAPI spec advatntage are:
* it can be easily loaded into AWS API Gateway and used in CloudFormation which in turn can save a ton of development effort
* it is a unified format that different teams / developers can learn and follow and be on the same page
* it has wonderful apps such as Readme to create interactive visual documentation 
