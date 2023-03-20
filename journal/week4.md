# Week 4 — Postgres and RDS

Mandatory Tasks
1. [Provision RDS Instance in CLI](#provision-rds-instance-in-cli)

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
