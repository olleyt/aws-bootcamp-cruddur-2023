# Week 10 — CloudFormation Part 1


### CloudFormation Designer
as a visual helper to help transform json to yaml

### Deploy with reviewing change set
./bin/cfn/deploy
/workspace/aws-bootcamp-cruddur-2023/aws/cfn/cluster/template.yaml

Waiting for changeset to be created..
Changeset created successfully. Run the following command to review changes:
aws cloudformation describe-change-set --change-set-name arn:aws:cloudformation:us-east-1:ACCOUNT_ID:changeSet/awscli-cloudformation-package-deploy-1685084449/fb229b2a-9090-4fcd-bf0d-a2f908221f56
### CFN Validate
aws cloudformation validate-template --template-body file:///workspace/aws-bootcamp-cruddur-2023/aws/cfn/cluster/template.yaml
{
    "Parameters": [],
    "Description": "Setup ECS Cluster\n"
}
### CFN Guard
```cfn-guard validate --data ./aws/cfn/cluster/template.yaml --rules ./aws/cfn/service/ecs-cluster.guard```
but nothing happened

cfn-guard validate \
--data ./aws/cfn/cluster \
--output-format yaml \
--rules ./aws/cfn/service/ecs-cluster.guard \
--show-summary pass,fail \
--type CFNTemplate

source: https://docs.aws.amazon.com/cfn-guard/latest/ug/cfn-guard-validate.html

### S3 bucket
create bucket named cfn-artifacts-<unique_id>
option  --s3-bucket $BUCKET will enable AWS to put the template file to the S3 bucket


## Networking Diagram
![physical_networking_diagram](../_docs/assets/week10/Cruddur-Networking-Page-2.drawio.svg)