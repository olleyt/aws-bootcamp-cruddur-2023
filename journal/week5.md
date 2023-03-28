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
