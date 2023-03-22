# Week 4 — Postgres and RDS

Mandatory Tasks
1. [RDS Security Best Practice](rds-security-best-practice)
2. [Provision RDS Instance in CLI](#provision-rds-instance-in-cli)
3. 

## RDS Security Best Practice
Watched Ashish's [video](https://www.youtube.com/watch?v=UourWxz7iQg&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=46)
Noted best practices for RDS:

1. create database in the region where data is compliant to be stored (e.g. GDPR)
2.master username is the database name to connect to
3.change default no encryption to encrypted database
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

create db/schema.sql file inside backend-flask folder and paste this line inside the file to add UUUID extension for PostgreSQL:
```
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

run the schema:
```
psql cruddur < db/schema.sql -h localhost -U postgres
```

if successful the command line will look like:
 ```
 gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ psql cruddur < db/schema.sql -h localhost -U postgres
Password for user postgres: 
CREATE EXTENSION
 ```

form a connection URL for postgreSQL:
```
export CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
```
set the environmental variable and test it works:
```
export CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
psql $CONNECTION_URL
```
response sjall look like:
```
psql (13.10 (Ubuntu 13.10-1.pgdg20.04+1))
Type "help" for help.

cruddur=# 
```

set gitpod env variable:
```
gp env CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
```
 
 THOSE STEPS ARE NOT EXECUTED:

set PROD_CONNECTION_URL at 1:05:00 - main video

create folder bin inside backend-flask
inside create 3 files without extensions:
- db-create
- db-drop
- db-schema-load

add ```#! /usr/bin/bash``` to the files and then make them executable for the user:
```bash
chmod u+x db-create db-drop db-schema-load 
```

run command in the terminal:
```bash
./bin/db-drop
```
expected response:
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
run command ``` ./bin/db-create ```
expected response:
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/db-create
db-create
CREATE DATABASE
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ 
```

edit file db-schema-load. Note that I had to add backend-flask folder into schema_path :
```
#! /usr/bin/bash
echo "db-schema load"

schema_path=$(realpath .)/backend-flask/db/schema.sql
echo $schema_path
psql $CONNECTION_URL cruddur < $schema_path
```
run command from the workspace/aws-bootcamp-cruddur-2023:
```
./backend-flask/bin/db-schema-load
```

response shall be:
```
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ ./backend-flask/bin/db-schema-load
db-schema load
/workspace/aws-bootcamp-cruddur-2023/backend-flask/db/schema.sql
CREATE EXTENSION
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ 
```
or work from backend-flask directory:
```bash
#! /usr/bin/bash
echo "db-schema load"

schema_path=$(realpath .)/db/schema.sql
echo $schema_path
psql $CONNECTION_URL cruddur < $schema_path
```

response:
```bash
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ cd backend-flask/
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ ./bin/db-schema-load
db-schema load
/workspace/aws-bootcamp-cruddur-2023/backend-flask/db/schema.sql
NOTICE:  extension "uuid-ossp" already exists, skipping
CREATE EXTENSION
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask (main) $ 

follow the commit history - add if statement for if statement and pretty colors

Next creating tables inside schema.sql

we add public in front of table names as default schema name for PostgreSQL

the table definition was based what was specified in Cruddur Open API and the mocked  data

create db-connect file:
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

create seed files, correct schema, re-run schema and then seed our data:
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

reminder that production connection url is not yet set.

connect to the local database  from backend-flask folder './bin/db-connect'
run ```\dt``` to see the tables

test the data is available inside the tables
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


create script db-connections

create script db-setup

the output on my new GitPod instance; the GitPod instance I created :
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

We will implement pooling withing the app.

add to requirements.txt
```
psycopg[binary]
psycopg[pool]
```
 install libraries:
 ```
 pip install -r requirements.txt
 ```
 add lib/db.py (commit)
 instrument home activities with PostgreSQL pooling (commit)
 
Andrew explained that for Cruddur project it would be best to return json in the app and pass it for further parsing rather than fetching all rows through cursor fetchall().

after making all the changes, we can see the first crud imported from seed data:
[screenshot]()

it's time to connect to AWS RDS now 
set PROD_CONNECTION_URL env variable in GitPod in this format:
```
export PROD_CONNECTION_URL="postgresql://<user>:<password>@<RDS endpoint>:5432/<master database name>"
```

if we are trying to connect with ```psql $PROD_CONNECTION_URL```, the command will just hang.

Go back to AWS RDS console and adjust security group inbound rules to allow Gitpod IP address to connect to our database 

Get the GitPod IP address with this command:
```
GITPOD_IP=$(curl ifconfig.me)
```
add allow rule on the RDS security group for the address that $GITPOD_IP holds.

run ```psql $PROD_CONNECTION_URL```:

then run \l and you shall see the list of databases .

Now to make our life easier, we will set environment variables for the security group and the inbound rule:
```
export DB_SG_ID=""
gp env DB_SG_ID=""
export DB_SG_RULE_ID=""
gp env DB_SG_RULE_ID=""
```

then we can utilise this CLI script below 
```
aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
```    
the expected response from the terminal:
```
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ aws ec2 modify-security-group-rules     --group-id $DB_SG_ID     --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
{
    "Return": true
}
```

create rds-update-sg-rule script inside bin folder:
```bash
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="rds-modify-inbound-rule"
printf "${CYAN}==== ${LABEL}${NO_COLOR}\n"

aws ec2 modify-security-group-rules \
    --group-id $DB_SG_ID \
    --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
    
execute : 
```bash 
chmod u+x rds-update-sg-rule
export GITPOD_IP=$(curl ifconfig.me)
./rds-update-sg-rule
```

check that the security group got updated in the AWS RDS console.

update gitpod.yml by adding command:
```yml
command: |
      export GITPOD_IP=$(curl ifconfig.me)
      source  "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds-update-sg-rule"
```

stop and start GitPod environment and check that rds-update-sg-rule executed successfully and then navigate to AWS RDS console and check that IP adress was updated on the incoming rule for the security group.

Update ./bin/db-connect to have a conditional statement for prod parameter.

Then we can check connectivity to the production database by running our connectivity script from backend-flask:
```
./bin/db-connect prod
```

check that we can see the databases with \l command.

However, we are still not able to connect to production database as we need to load the schema to the production instance. 

then go and load the schema from backend-flask folder:
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
