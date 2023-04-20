# Week 8 — Serverless Image Processing

## main stream

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
3. see that aws-cdk is version 2 in package.json
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
