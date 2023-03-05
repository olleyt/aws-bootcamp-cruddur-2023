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
    - username
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
