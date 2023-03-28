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
7. inside bin create folder 'ddb' and navidate there. 
8. create schema-load script inside 'ddb' folder
