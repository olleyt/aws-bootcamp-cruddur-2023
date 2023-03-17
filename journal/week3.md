# Week 3 — Decentralized Authentication

## Completed Required Homework
1. [Setup Cognito User Pool](#setup-cognito-user-pool)
2. [Instrument Amplify](#instrument-amplify)
3. [Implement Custom Signin Page](#implement-custom-signin-page)

## Setup Cognito User Pool
This is part was completed by following along [main lesson video for week 3](https://www.youtube.com/watch?v=9obl7rVgzJw&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=40):

Setting up a Cognito pool will be done in AWS console as it is the most reliable and easiest way to provision the pool for this project.

### AWS Console Steps for Creating a Cognito User Pool
1. Login into AWS Console (GUI)
2. Go to Cognito service
3. On the left hand side choose User Pools
4. Click on 'Create user pool' and then follow these steps for competing wizard steps:
- choose cognito user pool (default)
- Cognito user pool sign-in options, check the following:
    - email
- Click Next button
- on the 'Configure security requirements' page:
    - leave default  password policy although 16 character password length is better. Consider friction for your users
    - no MFA to save money as there is no free tier for MFA option
    - keep Self-service account recovery option enabled
    - click next
-  Configure sign-up experience
    - keep 'enable self-registration' checked (we don't know what it does and the text in the console is not clear)
    - keep 'Allow Cognito to automatically send messages to verify and confirm)
    - keep verifying via email, SMS will cost money
    - keep original attribute value active when update is pending
    - for required attributes choose: name, preferred name
- Configure Message Delivery: choose 'Send email with Cognito' (for now, we will implement integration with SES later)
- Integrate your app:
   - user pool name: cruddur-user-pool
   - keep Cognito hosted UI checkbox unchecked
   - application type: public client
   - application client name: Cruddur
   - don't generate a client secret. It's useful for client side but we will be using JWT token verification by Cruddur back-end  
   - click next 
- Review & create user pool   

I have also created a step by step guide with screenshots that can be accessed [here](https://olley.hashnode.dev/how-to-create-aws-cognito-user-pool) 

Then create a test user that will be used to implement and test authentication and authorization for this stage of the Cruddur project

## Instrument Amplify
We use Amplify Identity SDK library to use Cognito User Pool.

### GitPod Updates 

gitpod.yml: add to init phase:
```npm i aws-amplify --save```

or add command into gitpod.yml:
```
  - name: react-js
    command: |
      cd frontend-react-js
      npm i aws-amplify --save
```
### Front-end changes to instrument Amplify
1. add code in App.js as in Andrew's instructions but we don't need identity pool!
```js
import { Amplify } from 'aws-amplify';

Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
  "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
  "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
  "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
  "oauth": {},
  Auth: {
    // We are not using an Identity Pool
    // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
    region: process.env.REACT_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
    userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
    userPoolWebClientId: process.env.REACT_APP_AWS_USER_POOLS_WEB_CLIENT_ID,   // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
  }
});
```
2. add these env variables to frontend-js service in docker-compose.yml
```yml
      REACT_APP_AWS_PROJECT_REGION: "${AWS_DEFAULT_REGION}"
      REACT_APP_AWS_COGNITO_REGION: "${AWS_DEFAULT_REGION}"
      REACT_APP_AWS_USER_POOLS_ID: "<get from AWS Console>"
      REACT_APP_CLIENT_ID: "<get from AWS Console, App Intergration tab>"
```
3. set password for the created Cognito user in CLI:
```
aws cognito-idp admin-set-user-password \
  --user-pool-id <your-user-pool-id> \
  --username <username> \
  --password <password> \
  --permanent
```

### Implement Custom Signin Page


HomeFeedPage.js, DesktopNavigation.js, ProfileInfo.js, DesktopSidebar.js and Signin Page changes - take from commot history

## JWT Token Verification

### Python Code Cleanup
| Code Unit  |     Before      |  After |
|----------|:-------------:|------:|
| backend-flask/services/home_activities.py|  if cognito_user_id != None: | if cognito_user_id is not None: |
| col 2 is |    centered   |   $12 |
| col 3 is | right-aligned |    $1 |

## Resources used this week
[Comparing things to None the wrong way](https://docs.quantifiedcode.com/python-anti-patterns/readability/comparison_to_none.html)

