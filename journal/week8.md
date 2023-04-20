# Week 8 — Serverless Image Processing

## Implement CDK Stack

During main stream the instructors dicussed CDK constructs:
* L1 - primitive rocks, like cfnBucket
* L2 - more like a patterns with more than one AWS resource 
* L3 - a more opiniated patterns of more complex infrustructure and how resources are connected and interract with each other

Instructions:

1. In Gitpod, navigate to root of the workspace and then run these commands: 
```bash
mkdir thumbing-serverlsess-cdk
cd in this directory
npm install aws-cdk -g
```
2. initialise skeleton cdk project with TypeScript:
```
cdk init app --language typescript
```
![cdk_init](../_docs/assets/week8/cdk_install_init.png)
3. see that aws-cdk is version 2 in package.json: ![cdk_pakage_json](../_docs/assets/week8/cdk_pakage_json.png)
4. meat of this project will be sitting in ./lib folder
5. found the boiler plate thumbing-serverless-cdk-stack.ts script inside:
```ts
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class ThumbingServerlessCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // example resource
    // const queue = new sqs.Queue(this, 'ThumbingServerlessCdkQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });
  }
}

```
6. add code for creating s3 bucket
7. next we need to bootstrap CDK once for our account per region. From AWS [documentation](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html): "Bootstrapping is the process of provisioning resources for the AWS CDK before you can deploy AWS CDK apps into an AWS environment."(c):
```
cdk bootstrap "aws://ACCOUNT-NUMBER-1/REGION-1"
```
this command will run CDK bootstrapping. Note it suggests to pass role instead of using Admin role:
```
Using default execution policy of 'arn:aws:iam::aws:policy/AdministratorAccess'. Pass '--cloudformation-execution-policies' to customize.
```
8. Go to AWS Console -> CloudFormation -> Stacks and find stack CDKToolkit which is created for CDK itself
9. run command ```cdk deploy``` and this will generate ClodFormation template for our project. Note that cdk synth runs in background
![cdk_stack](../_docs/assets/week8/cdk_created_stacks.png)
we can also check the S3 bucket in on Resources tab:
![s3_bucket](../_docs/assets/week8/cdk_deployed_s3_bucket.png)
10. next we will create Lambda function for image processing
11. add ```.env``` for our environmnet variables but change name of the bucket name:
```
THUMBING_BUCKET_NAME='cruddur-thumbs-ot'
THUMBING_FUNCTION_PATH='/workspace/aws-bootcamp-cruddur-2023/aws/lambdas'
THUMBING_S3_FOLDER_INPUT='avatar/original'
THUMBING_S3_FOLDER_OUTPUT='avatar/processed'
```
12. load environment variables in our ts script by adding these lines:
```ts
//load env variables
const dotenv = require('dotenv')
dotenv.config()
```
13. run ```npm i dotenv``` - add this to gitpod.yml
14. run ```cdk synth```

Now we are continuiling on [video 72](https://www.youtube.com/watch?v=jyUpZP2knBI&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=72)
15. Andrew tried to delete our stack but it failed because the S3 bucket was not empty. He had to manually delete items in the bucket and then deleted our project stack. Leave CDKToolkit stack - do not delete it!
16. add 'before' task in gitpod.yml:
```yml
  - name: cdk
    before: |
      npm install aws-cdk -g
```      
17. we want to persist environment variables for CDK, so we will create .env.example file because .env is ignored by Git:
```
THUMBING_BUCKET_NAME='assets.architectingonaws.link'
THUMBING_FUNCTION_PATH='/workspace/aws-bootcamp-cruddur-2023/aws/lambdas/process-images'
THUMBING_S3_FOLDER_INPUT='avatar/original'
THUMBING_S3_FOLDER_OUTPUT='avatar/processed'
THUMBING_WEBHOOK_URL='api.architectingonaws.link/webhooks/avatar'
THUMBING_TOPIC_NAME='cruddur-assets'
```
Note that we are naming our S3 bucket specifically linked to our domain for CloudFront puprposes
18. copy files [from Andrew's repo](https://github.com/omenking/aws-bootcamp-cruddur-2023/tree/week-8-serverless-cdk/aws/lambdas/process-images) to GitPod environment
19. ```cd ../aws/lambdas/process-images/```
20. ```npm init -y```
21. ```npm install sharp```
22. ```npm i @aws-sdk/client-s3``` - CDK is broken into individual packages
23. Now it is time to try to deploy updated CDK stack, navigate back to the thumbing-serveress-cdk-stacks folder and run:
```
cdk synth
cdk deploy
```
24. navigate to AWS CloudFormation and observe that lambda was deployed:
![updated_cdk_stack](../_docs/assets/week8/updated_thumbing_cdk.png)

## Serve Avatars via CloudFront

[Stream Video 73](https://www.youtube.com/watch?v=Hl5XVb7dL6I&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=75)

We will create CloudFront distribution manually this time in AWS Console.
1. origin domain: assets s3 bucket. Shall I create this bucket before?
