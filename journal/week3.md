# Week 3 — Decentralized Authentication

## Completed Required Homework
1. [Setup Cognito User Pool](#setup-cognito-user-pool)
2. [Instrument Amplify](#instrument-amplify)
3. [Implement Custom Signin Page](#implement-custom-signin-page)
4. [Implement Custom Signup Page](#implement-custom-signup-page)
5. [Implement Custom Confirmation Page](#implement-custom-confirmation-page)
6. [Implement Custom Recovery Page](#implement-custom-recovery-page)
7. [Verify JWT token server side](#verify-jwt-token-server-side)
    * [Home Feed Page Changes ](#home-feed-page-changes)
    * [CORS headers update](#cors-headers-update)
    * [Update docker-compose](#update-docker-compose)
    * [Update Signup page](#update-signup-page)
    * [Remove JWT token when user signs out](remove-jwt-token-when-user-signs-out) 
    * [Add custom library for JWT token verification](#add-custom-library-for-jwt-token-verification)
    * [Instrument JWT token verification with custom library](#instrument-jwt-token-verification-with-custom-library)
    * [Add JWT verification to home activities](#add-jwt-verification-to-home-activities)
    * [Python Code Cleanup](#python-code-cleanup)
8. [Create Cruddur CSS theme](create-cruddur-css-theme)
9. [Watched Ashish's Week 3 - Decenteralized Authentication](https://www.youtube.com/watch?v=tEJIeII66pY&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=39)
10.[Watched about different approaches to verifying JWTs](https://www.youtube.com/watch?v=nJjbI4BbasU&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=43
)

However, I would need to learn more about JWT before attempting any challenges

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

## Implement Custom Signin Page

1. change cookie authentication to Amplify in line 7:

| Code Unit  | Line Number     |     Before      |  After  |
|------------|:---------------:|:---------------:|:-------:|
| frontend-react-js/src/pages/SigninPage.js|7|```import Cookies from 'js-cookie'```|``` import { Auth } from 'aws-amplify'; ```|

2. change block from line 16 from this:
```python
    event.preventDefault();
    setErrors('')
    console.log('onsubmit')
    if (Cookies.get('user.email') === email && Cookies.get('user.password') === password){
      Cookies.set('user.logged_in', true)
      window.location.href = "/"
    } else {
      setErrors("Email and password is incorrect or account doesn't exist")
```
to this:
```python
    setErrors('')
    event.preventDefault();
    Auth.signIn(email, password)
    .then(user => {
      localStorage.setItem("access_token", user.signInUserSession.accessToken.jwtToken)
      window.location.href = "/"
    })
    .catch (error =>  { catch (error) {
      if (error.code == 'UserNotConfirmedException') {
        window.location.href = "/confirm"
      }
      setErrors(error.message)
```

## Implement Custom Signup Page
Required changes for correct implementation can be seen through this [commit](https://github.com/olleyt/aws-bootcamp-cruddur-2023/commit/7384fbb6e7566339274cabdba2047af711ca3fdb)

## Implement Custom Confirmation Page
Required changes for correct implementationcan be seen through this [commit](https://github.com/olleyt/aws-bootcamp-cruddur-2023/commit/11f9809ee92383f81f7728ef72bd5bb02e1f4c3b)

## Implement Custom Recovery Page
Required changes for correct implementation can be seen through this [commit](https://github.com/olleyt/aws-bootcamp-cruddur-2023/commit/5755b2e5358637108824a7b85cf6aed28b6dd4f0)

## Verify JWT token server side
The JWT token is stored in browser's local storage, which will be used in authorization headers from the home page.

In order to verify JWT token correctly we need to implement changes outlined in the subsections below

### Home Feed Page Changes 
Authentication changes for instrumenting Amplify and Cognito  were made to HomeFeedPage.js, DesktopSidebar.js, ProfileInfo.js as can be seen in this [commit]([commit](https://github.com/olleyt/aws-bootcamp-cruddur-2023/commit/ba68e3830d70808a7faab6e3d751ca37c690f0fc) and this [commit](https://github.com/olleyt/aws-bootcamp-cruddur-2023/commit/ccb3cfff3f6747ce45a3dcd2eb12f61e3cddf4b9)


### CORS headers update
Back-end needs to be able to be able to accept correct CORS headers.
The required changes can be seen in this [commit](https://github.com/olleyt/aws-bootcamp-cruddur-2023/commit/bc9110bdd4ff4d7e523457ac545d06ccb88ca6d0)

### Update docker-compose

As per this [commit](https://github.com/olleyt/aws-bootcamp-cruddur-2023/commit/9513d2153a243b391c31bfef8aaa4eab8e06d70c), add these environment variables for your Cognito app and user pool:
```yml
AWS_COGNITO_USER_POOL_ID: "us-east-1_vBKMcxpJ9"
AWS_COGNITO_USER_POOL_CLIENT_ID: "7tp9c32crfu6hk1rdk43qiah33"
```

### Update Signup page

Update email to be username on frontend-react-js/src/pages/SignupPage.js:
```js
attributes: {
            name: name,
            email: username,
            preferred_username: username,
        },
```

### Remove JWT token when user signs out

Change try block to remove issued token from browser local storage in frontend-react-js/src/components/ProfileInfo.js like so:
```js
try {
        await Auth.signOut({ global: true });
        window.location.href = "/"
        localStorage.removeItem("access_token")
    } 
```

### Add custom library for JWT token verification
Initially Andrew was going to see if we can use Flask-AWSCognito library as-is, however there were certain limitations in its code that led to refactoring some of its code to Cruddur csurom library that we put in this file: backend-flask/lib/cognito_jwt_token.py

It was adapted for Cruddur specific purposes and the code can be seen in this [commit](https://github.com/olleyt/aws-bootcamp-cruddur-2023/commit/3bd01bb1830c83d4a467d2192f84ce7da958024e)

We also need to add this library ```python-jose``` to requirements.txt, install it with pip and restart Gitpod to pick up the changes.

### Instrument JWT token verification with custom library

Now we can use this library for the JWT token verification in backend-flask/app.py
The required changes to app.py can be seen in this [commit](https://github.com/olleyt/aws-bootcamp-cruddur-2023/commit/74acdc9ee39e19857ddb9f9e66abefce9139f5cc)

### Add JWT verification to home activities
This [commit](https://github.com/olleyt/aws-bootcamp-cruddur-2023/commit/ffc2d4dfa0fd580d43bebca714f369048400312d) applies changes to pass Cognito user details to home activities page.

Note: I added ClousWatch logging as well so there are two parameters are passed to HomeActivities instance:
- logger for Cloudwatch
- cognito_user_id

We also added an extra crud for when user authentication and authorization is sucessful:
```python
      # inserts an extra crud if a user was authenticated and authorized 
      if cognito_user_id != None:
        logger.info('Hey Cloudwatch! I am authorized to access /api/activities/home')
        extra_crud = {
          'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
          'handle':  'Lore',
          'message': 'My dear brother, it the humans that are the problem',
          'created_at': (now - timedelta(hours=1)).isoformat(),
          'expires_at': (now + timedelta(hours=12)).isoformat(),
          'likes_count': 1042,
          'replies': []
        }
        results.insert(0,extra_crud)
```

### Python Code Cleanup
| Code Unit  |     Before      |  After |
|----------|:-------------:|------:|
| backend-flask/services/home_activities.py|  if cognito_user_id != None: | if cognito_user_id is not None: |
|backend-flask/services/home_activities.py| likes | likes_count|
|requirements.txt|Flask-AWSCognito| removed Flask-AWSCognito as unnecessary dependency|
| app.py| import sys | removed as unnecessary dependency|
If you paid close attention you'd noticed that we need update 'likes' to 'likes_count' in that extra crud. ;)



## Create Cruddur CSS theme

Followed [the CSS video](https://www.youtube.com/watch?v=m9V4SmJWoJU&list=PLBfufR7vyJJ7k25byhRXJldB5AiwgNnWv&index=44) from the bootcamp playlist and copied Andrew's changes from his repository




## Resources used this week
[Comparing things to None the wrong way](https://docs.quantifiedcode.com/python-anti-patterns/readability/comparison_to_none.html)

