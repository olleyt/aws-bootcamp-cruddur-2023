# Week 3 — Decentralized Authentication

## Cognito User Pool
Main lesson video:
Login into AWS Console (GUI)
Go to Cognito
On the left hand side choose User Pools
Create user pool
- choose cognito user pool (default)
- Cognito user pool sign-in options, check the following:
    - email
    - username , preferred name
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
    - for required attributes choose: name
- Configure Message Delivery: choose 'Send email with Cognito' (for now)
- Integrate your app:
   - user pool name: cruddur-user-pool-ot (in case it is unique)
   - keep Cognito hosted UI checkbox unchecked
   - App type: public client
   - App Client Name: Cruddur
   - Don't generate a client secret (it's client side but it is for back-end); we will be using JWT token 
   - click next 
- Review & create user pool   

ADD SCRIBE instruction here.   

## Amplify GitPod
We use Amplify Identity SDK library to use Cognito User Pool

### Installation
GitPod: add to init phase:
```npm i aws-amplify --save```

or add command into gitpod.yml:
```
  - name: react-js
    command: |
      cd frontend-react-js
      npm i aws-amplify --save
```
### Configure Amplify
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

### Sign In Page
HomeFeedPage.js, DesktopNavigation.js, ProfileInfo.js, DesktopSidebar.js and Signin Page changes - take from commot history

