# Week 4 — Postgres and RDS

Mandatory Tasks
1. [RDS Security Best Practice](rds-security-best-practice)
2. [Provision RDS Instance in CLI](#provision-rds-instance-in-cli)
3. [Connect Gitpod to RDS instance part 1](#connect-gitpod-to-rds-instance-part-1)
4. [Create Schema for Postgres](#create-schema-for-postgres)
5. [Bash scripting for common database actions](#bash-scripting-for-common-database-actions)
6. [Install PostgreSQL Client](#install-postgresql-client)
7. [Connect Gitpod to RDS instance part 2](#connect-gitpod-to-rds-instance-part-2)
8. [Setup Cognito post confirmation lambda](#setup-cognito-post-confirmation-lambda)
9. [Creating Activities](#creating-activities)

## RDS Security Best Practice
Watched Ashish's [video](https://www.youtube.com/watch?v=UourWxz7iQg&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=46)
Noted best practices for RDS:

1. create database in the region where data is compliant to be stored (e.g. GDPR)
2. master username is the database name to connect to
3. change default no encryption to encrypted database
4. endponit and port are parts of the connection URL
5. better to set 'publicly accessible' field to 'No', however there are challenges for bootcamp with it, so will make it publically accessible
6. default security group inbound rule allows the database to talk only to itself. Later on we need to identify resources that will be allowed to connect to it. For bootcamp purposes, choose My IP
7. enable deletion protection
8. enable multi-AZ for production workloads 
9. delete database if you are not using it or create a snapshot and restore database from it
10. create SCP to deny production database modifications / deletion, region lock, encryption
11. prod environment - enable GuarDuty to protect against malicious activities
12. prod environment - enable CloudTrail
13. use apporopriate authentofication 
14. encryption in transit between the app and db
15. use secret manager for database master password and automatically rotate secrets with it



## Provision RDS Instance in CLI

Refer to the official [CLI documentation](https://docs.aws.amazon.com/cli/latest/reference/rds/create-db-instance.html)

```
aws rds create-db-instance \
  --db-instance-identifier cruddur-db-instance \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version  14.6 \
  --master-username <change> \
  --master-user-password <change> \
  --allocated-storage 20 \
  --availability-zone <change> \
  --backup-retention-period 0 \
  --port 5432 \
  --no-multi-az \
  --db-name cruddur \
  --storage-type gp2 \
  --publicly-accessible \
  --storage-encrypted \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --no-deletion-protection
```

use Secret Manager instead and run the command in AWS CloudShell to save on GitPod credits:
```
aws rds create-db-instance \
  --db-instance-identifier cruddur-db-instance \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version  14.6 \
  --master-username <CHANGE_PASSWORD> \
  --manage-master-user-password \
  --allocated-storage 20 \
  --availability-zone us-east-1a \
  --backup-retention-period 0 \
  --port 5432 \
  --no-multi-az \
  --db-name cruddur \
  --storage-type gp2 \
  --publicly-accessible \
  --storage-encrypted \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --no-deletion-protection
```

Then go to Gitpod, run docker-compose up and check that we can still connect to PostreSQL instance from PostgreSQL container:
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ psql -Upostgres -h localhost
```

### Create and drop Cruddur database

create database from psql command line:
```sql CREATE database cruddur; ```

run \l command and observe the database was created:
```
postgres=# CREATE database cruddur;
CREATE DATABASE
postgres=# \l
                                 List of databases
   Name    |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges   
-----------+----------+----------+------------+------------+-----------------------
 cruddur   | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
 postgres  | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
 template0 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
(4 rows)
```

## Create Schema for Postgres

1. Create db/schema.sql file inside backend-flask folder and paste this line inside the file to add UUUID extension for PostgreSQL:
```
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```
UUID is a unique long identifier that can serve as a primary key in a database table. 
UUID is also a complex and lengthy identifier, so bad hats will have hard times guessing how many users are in our database. 

2. Full code for schema.sql where we create two tables for user and their activities:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS public.users;
CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  display_name text NOT NULL,
  handle text NOT NULL,
  email text NOT NULL,
  cognito_user_id text NOT NULL,
  created_at TIMESTAMP default current_timestamp NOT NULL
);

DROP TABLE IF EXISTS public.activities;
CREATE TABLE public.activities (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_uuid UUID NOT NULL,
  message text NOT NULL,
  replies_count integer DEFAULT 0,
  reposts_count integer DEFAULT 0,
  likes_count integer DEFAULT 0,
  reply_to_activity_uuid integer,
  expires_at TIMESTAMP,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```

3. Next, navigate to backend-flask folder in the terminal and run the schema:
```
psql cruddur < db/schema.sql -h localhost -U postgres
```

if successful the terminal output will look like:
 ```
 gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ psql cruddur < db/schema.sql -h localhost -U postgres
Password for user postgres: 
CREATE EXTENSION
 ```
## Connect Gitpod to RDS instance part 1 
### Setting environment variables
Next we will form a connection URL for postgreSQL and set it as an environment variable for local PostgreSQL instance running as a container on GitPod:
```
export CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
```
set the environmental variable and test it works:
```
export CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
psql $CONNECTION_URL
```

Response from the terminal shall look like:
```
psql (13.10 (Ubuntu 13.10-1.pgdg20.04+1))
Type "help" for help.

cruddur=# 
```

set gitpod env variable:
```
gp env CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
```
 
Now we need to set PROD_CONNECTION_URL as explained at 1:05:00 - [main video](https://www.youtube.com/watch?v=EtD7Kv5YCUs&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=46)
The production connection string will not be exposed here for security reasons.

## 	Bash scripting for common database actions

### db-create, db-drop, and db-schema-load
1. Create folder bin inside backend-flask
2. Navigate inside bin directory and create 3 files without extensions:
- [db-create](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/4e3e5022dc87159c31fd5ae0438302af844fd700/backend-flask/bin/db-create)
- [db-drop](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/4e3e5022dc87159c31fd5ae0438302af844fd700/backend-flask/bin/db-drop)
- [db-schema-load](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/4e3e5022dc87159c31fd5ae0438302af844fd700/backend-flask/bin/db-schema-load)

3. add ```#! /usr/bin/bash``` to the files and then make them executable for the user:
```bash
chmod u+x db-create db-drop db-schema-load 
```
4. run command in the terminal:
```bash
./bin/db-drop
```
5. expected response:
```bash
itpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/db-drop
db-drop
DROP DATABASE
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ 
```

edit db-create file like so:
```bash
#! /usr/bin/bash

echo "db-create"

NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "create database cruddur;"
```
6. run command ``` ./bin/db-create ```
expected response:
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/db-create
db-create
CREATE DATABASE
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ 
```

7. edit file db-schema-load. Note that I had to add backend-flask folder into schema_path :
```
#! /usr/bin/bash
echo "db-schema load"

schema_path=$(realpath .)/backend-flask/db/schema.sql
echo $schema_path
psql $CONNECTION_URL cruddur < $schema_path
```
8. run command from the workspace/aws-bootcamp-cruddur-2023:
```
./backend-flask/bin/db-schema-load
```

9. response shall be:
```
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ ./backend-flask/bin/db-schema-load
db-schema load
/workspace/aws-bootcamp-cruddur-2023/backend-flask/db/schema.sql
CREATE EXTENSION
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ 
```
10. alternatively work from backend-flask directory:
```bash
#! /usr/bin/bash
echo "db-schema load"

schema_path=$(realpath .)/db/schema.sql
echo $schema_path
psql $CONNECTION_URL cruddur < $schema_path
```

11. expected response from the terminal:
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ cd backend-flask/
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/db-schema-load
db-schema load
/workspace/aws-bootcamp-cruddur-2023/backend-flask/db/schema.sql
NOTICE:  extension "uuid-ossp" already exists, skipping
CREATE EXTENSION
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ 
```

12. We did some refactoring for loading schems:
- added if-else statement for switching between connecting to RDS (prod) and local PostgreSQL instance running on a Docker container
- added pretty colors for terminal logging
- added creating tables statements inside schema.sql
- added public in front of table names as default schema name for PostgreSQL

Note: the table definition was based what was specified in Cruddur Open API and the mocked  data

### db-connect
13. create db-connect file:
```
#! /usr/bin/bash

psql $CONNECTION_URL
```

check that tables are present:
```
cruddur=# \dt
           List of relations
 Schema |    Name    | Type  |  Owner   
--------+------------+-------+----------
 public | activities | table | postgres
 public | users      | table | postgres
```
#### seed.sql
14. Create [seed sql file](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/4e3e5022dc87159c31fd5ae0438302af844fd700/backend-flask/db/seed.sql) and [db-seed bash script](https://github.com/olleyt/aws-bootcamp-cruddur-2023/tree/main/backend-flask/bin), correct schema, re-run schema and then seed our data:
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ git status
On branch main
Your branch is up to date with 'origin/main'.

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        db/seed.sql

nothing added to commit but untracked files present (use "git add" to track)
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ chmod u+x db/seed.sql
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/db-schema-load 
== db-schema-load
db-schema load
/workspace/aws-bootcamp-cruddur-2023/backend-flask/db/schema.sql
this is dev
NOTICE:  extension "uuid-ossp" already exists, skipping
CREATE EXTENSION
DROP TABLE
CREATE TABLE
DROP TABLE
CREATE TABLE
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/db-seed
bash: ./bin/db-seed: Permission denied
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ chmod u+x ./bin/db-seed
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/db-seed
== db-seed
db-seed
/workspace/aws-bootcamp-cruddur-2023/backend-flask/db/seed.sql
this is dev
INSERT 0 2
INSERT 0 1
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ 
```

15. connect to the local database  from backend-flask folder './bin/db-connect'
run ```\dt``` to see the tables

16. test the data is available inside the tables
```sql
SELECT
        activities.uuid,
        users.display_name,
        users.handle,
        activities.message,
        activities.replies_count,
        activities.reposts_count,
        activities.likes_count,
        activities.reply_to_activity_uuid,
        activities.expires_at,
        activities.created_at
      FROM public.activities
      LEFT JOIN public.users ON users.uuid = activities.user_uuid
      ORDER BY activities.created_at DESC
```      
### db-connections
17. create script [db-connections](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/4e3e5022dc87159c31fd5ae0438302af844fd700/backend-flask/bin/db-connect) to see active sessions connected to the database
### db-setup
18. create script [db-setup](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/main/backend-flask/bin/db-setup) to speed up our workflow from dropping existing database, recreating the database and the tables, loading schema and seeding mock data.
19. Test the db-setup script. The output on my new GitPod instance; the GitPod instance I created :
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/db-setup 
./bin/db-setup: line 2: -e: command not found
==== db-setup
== db-drop
db-drop
ERROR:  database "cruddur" does not exist
== db-create
db-create
CREATE DATABASE
== db-schema-load
db-schema load
/workspace/aws-bootcamp-cruddur-2023/backend-flask/db/schema.sql
this is dev
CREATE EXTENSION
NOTICE:  table "users" does not exist, skipping
DROP TABLE
CREATE TABLE
NOTICE:  table "activities" does not exist, skipping
DROP TABLE
CREATE TABLE
== db-seed
db-seed
/workspace/aws-bootcamp-cruddur-2023/backend-flask/db/seed.sql
this is dev
INSERT 0 2
INSERT 0 1
```

## Install PostgreSQL Client

We will implement database pooling withing the app.

1. add psycopg libraries to requirements.txt
```
psycopg[binary]
psycopg[pool]
```
2. install libraries:
 ```
 pip install -r requirements.txt
 ```
 
3. create [lib/db.py](../backend-flask/lib/db.py) as a utility library for running SQL queries on RDS.
4. instrument home activities with PostgreSQL pooling. Note that below I posted the final refactored code after we abstracted loading SQL in a template and executing SQL query in db.py
```python
      sql = db.load_template('activities','home')
      params = {}
      results = db.query_array_json(sql, params)
       # span.set_attribute("app.result-length", len(results))
      return results
```
 
Andrew explained that for Cruddur project it would be best to return json in the app and pass it for further parsing rather than fetching all rows through cursor fetchall().

5. After making all the changes, we can see the first crud imported from seed data:
![screenshot](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/91069fb29e661c41d5316cdf6b7ca496a99e6d86/_docs/assets/seed_data.png)

## Connect Gitpod to RDS instance part 2
6. It's time to connect to AWS RDS now. 
set PROD_CONNECTION_URL env variable in GitPod in this format:
```
export PROD_CONNECTION_URL="postgresql://<user>:<password>@<RDS endpoint>:5432/<master database name>"
gp env PROD_CONNECTION_URL="postgresql://<user>:<password>@<RDS endpoint>:5432/<master database name>"
```

7. If we are trying to connect with ```psql $PROD_CONNECTION_URL```, the command will just hang because default security group on our RDS instance is not allowing inbound access to anyone except the security group itself.  

8. Go back to AWS RDS console and adjust security group inbound rules to allow Gitpod IP address to connect to our database 
Get the GitPod IP address with this command:
```
GITPOD_IP=$(curl ifconfig.me)
```
add allow rule on the RDS security group for the address that $GITPOD_IP holds.

9. run ```psql $PROD_CONNECTION_URL```:

10. then run \l and you shall see the list of databases .

11. Now to make our life easier, we will set environment variables for the security group and the inbound rule:
```
export DB_SG_ID=""
gp env DB_SG_ID=""
export DB_SG_RULE_ID=""
gp env DB_SG_RULE_ID=""
```

12. then we can utilise this CLI script below 
```
aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
``` 

13. the expected response from the terminal:
```
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ aws ec2 modify-security-group-rules     --group-id $DB_SG_ID     --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
{
    "Return": true
}
```

14. create rds-update-sg-rule script inside bin folder:
```bash
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="rds-modify-inbound-rule"
printf "${CYAN}==== ${LABEL}${NO_COLOR}\n"

aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
    
15 execute the below lines in the terminal: 
```bash 
chmod u+x rds-update-sg-rule
export GITPOD_IP=$(curl ifconfig.me)
./rds-update-sg-rule
```

16. check that the security group got updated in the AWS RDS console.

17. update gitpod.yml by adding command:
```yml
command: |
      export GITPOD_IP=$(curl ifconfig.me)
      source  "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds-update-sg-rule"
```

18. stop and start GitPod environment and check that rds-update-sg-rule executed successfully and then navigate to AWS RDS console and check that IP adress was updated on the incoming rule for the security group.

19. Update ./bin/db-connect to have a conditional statement for prod parameter.

20. Then we can check connectivity to the production database by running our connectivity script from backend-flask:
```
./bin/db-connect prod
```

21. check that we can see the databases with \l command.
However, we are still not able to connect to production database as we need to load the schema to the production instance. 

22. go to backend-flask folder and load the schema to the RDS instance:
```
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/db-schema-load prod
== db-schema-load
db-schema load
/workspace/aws-bootcamp-cruddur-2023/backend-flask/db/schema.sql
this is prod
CREATE EXTENSION
NOTICE:  table "users" does not exist, skipping
DROP TABLE
CREATE TABLE
NOTICE:  table "activities" does not exist, skipping
DROP TABLE
CREATE TABLE
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ 
```

## Setup Cognito post confirmation lambda

### Create the Lamba function
1. Create Lambda with boiler plate code in AWS management console, name it 'cruddur-confirmation-function' and choose Python 3.8 as runtime. Leave other settings with default values
2. assign default execution role and add AWS managed policy AWSLambdaVPCAccessExecutionRole to this role to give permission to create ENI. See details why we need it [here](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html#vpc-permissions) 
4. attach the lambda function to VPC following this [guide from AWS](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html)
5. add a layer with this ARN: ```arn:aws:lambda:us-east-1:898466741470:layer:psycopg2-py38:1 doesn't work, arn:aws:lambda:us-east-1:898466741470:layer:psycopg2-py38:2``` ; got it from this [GitHub post](https://github.com/jetbridge/psycopg2-lambda-layer/issues/23)
6. rewrite boiler plate code for Lambda function to insert a user into PostgreSQL AWS RDS on user sign up:
```python
import json
import psycopg2
import os

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    user_display_name  = user['name']
    user_email         = user['email']
    user_handle        = user['preferred_username']
    user_cognito_id    = user['sub']
    
    sql = f"""
      INSERT INTO public.users(
        display_name,
        email, 
        handle, 
        cognito_user_id)
      VALUES ( %s, %s, %s, %s)
    """

    params = [user_display_name, user_email, user_handle, user_cognito_id]
    
    try:
        conn = psycopg2.connect(os.getenv('CONNECTION_URL'))
        cur = conn.cursor()
        cur.execute(sql, *params)
        conn.commit() 

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        
    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print('Database connection closed.')

    return event
```

6. add Lambda layer for psycopg2 : ```arn:aws:lambda:us-east-1:898466741470:layer:psycopg2-py38:2``` . Note it's not verifiable and can pose a security risk but can be good enough for our learning project
7. add AWS Lambda environment variable CONNECTION_URL from GitPod by env | grep PROD
8. add trigger on lambda from our Cognito user pool. Go to the AWS Cognito, choose cruddur user pool and go to 'user pool properties' tab
9. trigger type 'Sign Up', Sign Up option 'post confirmation trigger', choose the created lambda function in 'Assign Lambda function' drop down list 
10. deploy lambda code in the AWS Lambda console by clicking on 'Deploy' button.

Test lambda handler by signing up a new user:
1. run docker-compose up on GitPod
2. update the schema on production database with ```./bin/db-schema-load prod```
3. go to the Cruddur web app and sign up a new user
4. check that CloudWatch logs had no errors
5. check database table contains a user: ```./bin/db-connect prod```
```
\x on
select * from users
```
Response:
```bash
cruddur=> \x on
Expanded display is on.
cruddur=> select * from users;
-[ RECORD 1 ]---+-------------------------------------
uuid            | 4c5c16bf-5959-4305-9e00-bfa770082a7b
display_name    | Olley T
handle          | olleyt2
email           | does-not-exist@gmail.com
cognito_user_id | be8129b4-714c-4c1a-a2bd-9dbc59557e8f
created_at      | 2023-03-24 10:37:28.784121
```

woohoo! it works! but our job is not done yet as we need to instrument create_activity.py to create and show activity feed.

## Creating Activities

Next we will implement creating new activities with a database insert.

### Pre-requisites
1. start your RDS instance
2. launch GitPod for correct branch (main)
3. run docker-compose up
4. go to back-end flask folder
5. run ```./bin/db-connect``` to ensure that connection to RDS is not hanging

### SQL templates
1. Create sql/activities folders inside ./backend-flask/db like so:
```bash
./backend-flask/
│
└── sql/
    └── activities
```
2. inside activities: create [home.sql](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/91069fb29e661c41d5316cdf6b7ca496a99e6d86/backend-flask/db/sql/activities/home.sql) for getting array of cruds to show as home activity feed,
3. [create.sql](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/91069fb29e661c41d5316cdf6b7ca496a99e6d86/backend-flask/db/sql/activities/create.sql) for inserting a new activity to the database,
4. [and object.sql](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/91069fb29e661c41d5316cdf6b7ca496a99e6d86/backend-flask/db/sql/activities/object.sql) for showing the created CRUD on the feed for the user who just created it.


### Changes for create_activities.py
Add these two methods at the end of the class:
```python
   def create_activity(handle, message, expires_at):
        """
        this method creates a crud and commits in RDS
        """
        sql = db.load_template('activities', 'create')
        params = {'handle': handle, 'message': message,
                  'expires_at': expires_at}
        user_uuid = db.query_commit(sql, params)
        return user_uuid

    def query_object_activity(activity_uuid):
        """
        select crud data to show on front-end
        """
        sql = db.load_template('activities', 'object')
        params = {'uuid': activity_uuid}
        return db.query_object_json(sql, params)
```

Substitute mocked data with creating a CRUD and showing it on the feed around line 50 in the run() function, last else block:
```python
        else:
            expires_at = (now + ttl_offset).isoformat()
            created_activity_uuid = CreateActivity.create_activity(user_handle, message, expires_at)

            object_json = CreateActivity.query_object_activity(created_activity_uuid)
            model['data'] = object_json
        return model
```

Note: there could be other minor changes and I would recommend to do diff compare between week 3 and week 4 commits

#### Changes to home_activities.py
```python

from datetime import datetime, timedelta, timezone
from opentelemetry import trace

#from lib.db import pool, query_wrap_array
from  lib.db import db

tracer = trace.get_tracer("home.activities")

class HomeActivities:
  def run(logger, cognito_user_id=None):
    logger.info('Hello Cloudwatch! from  /api/activities/home')
    with tracer.start_as_current_span("home-activities-mock-data"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())

      sql = db.load_template('activities','home')
      params = {}
      results = db.query_array_json(sql, params)
       # span.set_attribute("app.result-length", len(results))
      return results
```

### Passing User Handle from Front End
This solution was advised by anle4s in the bootcamp Discord [thread](https://discord.com/channels/1055552619441049660/1086233246691495968).
I think this is a great implementation and following the bootcamper instructions to properly pass the user handle instead of hardcoding it in app.py

1. Update the ActivityForm component in pages/HomeFeedPage.js to pass the user_handle prop as follows:
```js
<ActivityForm
  user_handle={user}
  popped={popped}
  setPopped={setPopped}
  setActivities={setActivities}
/>
```
2. In the components/ActivityForm.js component, update the fetch request body to include the user_handle:
```js
body: JSON.stringify({
  user_handle: props.user_handle.handle,
  message: message,
  ttl: ttl
}),
```

3. In app.py, under the /api/activities route, assign the user_handle variable as follows:
```python
user_handle = request.json["user_handle"]
```

Save, commit and push.
Then start the RDS and run docker-compose up and test posting a crud.

This is the end result of week 4:
![completed_week4_screenshot](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/91069fb29e661c41d5316cdf6b7ca496a99e6d86/_docs/assets/final_rds_data.png)

#### Testing and Troubleshooting

#### PostConfirmation failed with error
check:
- RDS is running
- GITPOD_IP matches IP address on the RDS default security group 
- Lambda connection url is correct
- password for CONNECTION_URL matches current Secret Manager secret both on GitPod and Lambda variables

#### Other Errors
There will be flood of errors like this because of Chrome extensions like EverNote: 
``` commons.js:2 Channel: Error in handleResponse UNK/SW_UNREACHABLE isLogsEnabled null
handleResponsePromise @ commons.js:2
```

```Database cruddur does not exists``` - this error came from the local PostgreSQL container when I switched GitPod instances and didnot re-create a local database.
I changed docker compose file to set ```CONNECTION_URL = "${PROD_CONNECTION_URL}"```

Note: Secret Manager will rotate RDS secrets every 7 days so environment variables for CONNECTION_URL and PROD_CONNECTION_URL as well as Lambda environment variable need to be refreshed. 

DesktopNavigationLink.js throws warnings but I giuess we will re-implement that later.

## Useful resources
- [Pathlib library](https://docs.python.org/3/library/pathlib.html)
- [Amazon RDS Proxy](https://aws.amazon.com/rds/proxy/)
- [Using Secrets Manager](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/secrets-envvar-secrets-manager.html)
- [How can I pass secrets or sensitive information securely to containers in an Amazon ECS task?](https://aws.amazon.com/premiumsupport/knowledge-center/ecs-data-security-container-task/)
- [How to Manage Secrets for Amazon EC2 Container Service–Based Applications by Using Amazon S3 and Docker](https://aws.amazon.com/blogs/security/how-to-manage-secrets-for-amazon-ec2-container-service-based-applications-by-using-amazon-s3-and-docker/)
- [Create an AWS Secrets Manager database secret](https://docs.aws.amazon.com/secretsmanager/latest/userguide/create_database_secret.html)
- [Password management with Amazon RDS and AWS Secrets Manager](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-secrets-manager.html#rds-secrets-manager-db-instance)
