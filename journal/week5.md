# Week 5 — DynamoDB and Serverless Caching


## Dynamo DB Security Considerations
1. Protect from public access: use VPC endpoints, or site-to-site VPN, direct connect for on-prem access
2. Compliance standard depends on what your organisation requires
3. Use CloudTrail to monitor malicious activity. DynamoDb is still not monitired by GuardDuty
4. Create DynamoDb tables in region(s) you can legally store data (think about regulations like GDPR)
5. Set SCP guardrails for your organisation on DynamoDB actions; i.e. prevent deletions
6. Configure AWS Config Rules for additional security
7. Use apprpriate access IAM polices and roles to give access to only people and services reuiring it
8. Prefer using roles and short living credentials like roles or Cognito Identity pools instead of IAM users / groups 
9. AWS recommends to use client side encryption
10. try to limit DAX to read access role only if possible 

## Design Considerations
## DynamoDB Utility Scripts

### Install Boto3
1. add boto3 in requirements.txt
2. pip install it.

### House Keeping
3. run docker-compose up to run DynamoDb on local containers.
4. inside bin create folder 'db' and move all scripts starting with 'db-' there, and then remove this prefix.
5. inside bin create folder 'rds' and move script that updates default RDS security group in that folder.
6. setup script needs updates
7. inside bin create folder 'ddb' and navigate there. 
8. create scripts inside 'ddb' folder:
    * schema-load
    * drop
    * seed
    * list-tables

9. create DynamoDB local table with [AWS SDK Boto3 for DynamoDB](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html)
go to ./ddb/schema-load file and edit it like so:
```bash
#! /usr/bin/env python3

<COPY FROM MY VSCODE>

```
10. save it and run chmod u+x on it. 

11. run in terminal 
```
./bin/ddb/schema-load
```

12. create script ```list tables``` inside ddb folder so we can verify and query our table:
```bash
#! /usr/bin/bash
set -e # stop if it fails at any point

if [ "$1" = "prod" ]; then
  ENDPOINT_URL=""
else
  ENDPOINT_URL="--endpoint-url=http://localhost:8000"
fi

aws dynamodb list-tables $ENDPOINT_URL \
--query TableNames \
--output table
```

chmod the script u+x and run in the terminal : ```./bin/ddb/list-tables```

## Resources:
- [Python args vs kwargs](https://realpython.com/python-kwargs-and-args/)
