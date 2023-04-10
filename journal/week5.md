# Week 5 — DynamoDB and Serverless Caching

Contents:
1. [Deviations from official guidance](#deviations-from-official-guidance)
2. [Dynamo DB Security Considerations](#dynamodb-security-considerations)
3. [Design Considerations](#design-considerations)
4. [DynamoDB Utility Scripts](#dynamodb-utility-scripts)
5. [Create New Conversation](#create-new-conversation)
6. [Create New Message](#create-new-message)
7. [Implementing DynamoDB Streams](#implementing-dynamodb-streams)
8. [Troubleshooting](#troubleshooting)
9. [Resources](#resources)

## Deviations from official guidance

* some Python code has 4 spaces identation: db.py
* postgreSQL scripts in db folder still have *db-* prefix
* script that updates default security group still have *rds* prefix
* I run RDS as production instance for since week 4 and stopped used mocked data but instead used my own 3 users I signed up in Cruddur
* my function to load sql scripts called 'load_template' in db.py instead of 'template'
* Andrew added his 3rd user Londo Mollari to seed data script. I added a new user by signing it up in Cruddur on a separate email account so it was stored in RDS and registered in Cognito User pool

## DynamoDB Security Considerations
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
‘Access patterns dictate everything’ - Kirk Kirkconell

The below text is my study notes from the [live stream](), so there could be sentences that are matching exact conversation between Andrew and Kirk.

### NoSQL Data Modelling Considerations
Preplanning is critical for NoSQL data modelling. Dumping data can lead to expensive solutions or solutions that do not perform well.
NoSQL databases perform their best when getting data as precomputed output.

We shall think about organising data for NoSQL database as the precomputed output for the application and in a sense:
 * what data do we need
 * when 
 * at what velocity data will be accessed.

Kirk's advice:
* Think about NoSQL queries as if you were getting data from a single flat table. 
* When designing a flat table think about what are related attributes that can be accessed together. For example, what data is also related to conversations like time it was created at, users involved.
* Storage is cheap, so that it is perfectly fine to have duplicated attributes in the base table if it is supporting access patterns. DynamoDB has consistent low latency.
* We are asking NoSQL ‘go get me data’ instead of deriving insights from the data in traditional SQL way. This allows DynamoDB to have consistent performance at millisecond time.
* We are not asking questions of data because we know what data we need to get exactly and that’s why we want it pre-computed and stored in a flat structure for easy access.

Side note: some people like to get data from NoSQL in SQL fashion. PartiQL can help with that.

### DynamoDB Data Presentation with GSI and LSI
We can slice and dice data from the base flat table as if we were looking at different facets of a crystal with using global secondary indices (GSI) or local secondary indices(LSI).
* GSI: eventually consistent global secondary index. We can choose subsets of attributes from the base table to project and it acts as another optimised table for a specific access patterns allowing to save on cost due to attribute optimisation. Items in GSIs do not need to be unique and that’s why we cannot use get_iem() operation but can only query or scan items. Another way to describe a GSI is it is a different view of the same data.
* LSI: strong consistent local secondary index where data stored and ordered in a different way compared to the base table. We can slice and dice data whatever way we want to support our access patterns.  LSI is created at table creation time and cannot be created or deleted afterwards.

### Base Table Design
Base table shall be designed to support as many access patterns as possible while keeping amount of  GSI and LSI to minimum. We shall solve 80-90% access patterns with the base table and 20-10% with GSI ( and maybe LSI).

Base table + GSI can be a comparable Dynamo DB cost for having two DynamoDB tables for our application.

As Kirk said, “with RDS we model tables as database wants it whereas NoSQL database allow to model as application will interact with the data”.

### DynamoDB Constraints 
* _partition key_ is mandatory for querying table. We need to design base table in a way that data is evenly distributed across partition key values
* if a table was created with a _sort key_ then we can use it for querying. Sort key is optional when querying DynamoDB table

As mentioned in the ‘DynamoDB book’, some people make general names for partition key as ‘pk’ and sort key as ‘sk’ because of pivoting data for different access patterns can make naming keys hard. They also duplicate these ‘pk’ and ‘sk’ as explicit attributes to support design flat table for as many access patterns as possible while keeping least amount of GSIs and LSIs.

In addition to that, some people create a ‘data’ key and dump entire record in that attribute in JSON format for performance reasons.

### Cruddur Flat NoSQL Table
* We put Cruddur message and conversation data in one flat table because it is related.
* We are also reducing database management complexity compared to multi-table database approach:
    * think about balancing multi indexes
    * replicating one global table for disaster recovery purposes is a lot easier than replicating multiple tables and ensure that all data is in sync  

### Cruddur Patterns
#### Note about uuid
Applications usually cannot piece together data in a picture based on uuid. 
However, for Cruddur it will work very well as  we want to obscure how many users we have.

#### Pattern A: conversations with others (message groups). 
This access pattern is ‘What conversations I am in with others’ that shall show message groups. This access pattern shall be able to grab most recent conversations for the user and they shall be shown in a descendent order.

#### Pattern B: Show all messages that are in a conversation and sort messages by ‘created_at’ attribute in descendent order. 
- Andrew asked Kirk if there is an order we shall follow to review our access patterns? 
- Kirk advised: “We shall get Message Groups data from the base table. However,  getting into a message group is a less frequent pattern).” 
We can also put additional attributes in a JSON string if wea re not going to index on those attributes.
- Andrew replied that it is an interesting idea and we might should have follow that but it is too late to re-design Cruddur. 
When we create a message in a conversation, we might need 2 message groups:
    - one from the logged in user perspective
    - other one is for the user our logged in user is interacting with and having conversation.
Hence we need to add other_user_uuid in the base table

#### Pattern C: create message 
Our flat table design was already supporting this access pattern

#### Pattern D: reply to existing conversation and update relevant message groups

The hardest part of this pattern was getting the last replier and the related message to update both message groups. We probably would need to delete and re-create the record in our base table because we would need to know ‘pk’ and ‘sk’ of the record to update it in one go. We can also update only 1 record at a time in DynamoDB so probably one update operation is not feasible anyways. 
Perhaps this is the reason why we need a GSI for current Cruddur base table design.

#### Missing Patterns
- Pagination: we could have limit number of returned items while refining results for Pattern B. Kirk suggested to narrow down the refined result.
- Update display name: this would require updating all related messages and conversations. It’s too late to cater for this pattern and we are not going to implement it

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
    * delete-table
    * seed
    * list-tables

9. create DynamoDB local table with [AWS SDK Boto3 for DynamoDB](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html)
go to ./ddb/schema-load file and edit it like so:
```bash
import sys
import boto3

kwargs = {
  'endpoint_url': 'http://localhost:8000'
}

if len(sys.argv) == 2:
    if "prod" in sys.argv[1]:
        kwargs = {}
    
ddb = boto3.client('dynamodb', **kwargs)

table_name = 'cruddur-messages'

response = ddb.create_table(
    TableName =  table_name,
    AttributeDefinitions=[
        {
            'AttributeName': 'pk',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'sk',
            'AttributeType': 'S'
        },
    ],
    KeySchema=[
        {
            'AttributeName': 'pk',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'sk',
            'KeyType': 'RANGE'
        },
    ], 
    # add GSI later
    BillingMode='PROVISIONED',
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    },
    Tags=[
        {
            'Key': 'string',
            'Value': 'string'
        },
    ]
)

print(response)

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

13. create drop script which I renamed as delete-table:
```bash
#! /usr/bin/bash

set -e # stop if it fails at any point

if [ -z "$1" ]; then
  echo "No TABLE_NAME argument supplied eg ./bin/ddb/drop cruddur-messages prod "
  exit 1
fi
TABLE_NAME=$1

if [ "$2" = "prod" ]; then
  ENDPOINT_URL=""
else
  ENDPOINT_URL="--endpoint-url=http://localhost:8000"
fi

echo "deleting table: $TABLE_NAME"

aws dynamodb delete-table $ENDPOINT_URL \
  --table-name $TABLE_NAME
```

14. chmod u+x and then run this command to test it from ./backend-flask/bin/ddb folder: ```./delete-table cruddur-messages```
15. it is important to have 2 users in our Cognito user pool and users' uuid shall come from the database
16. Sign up second user to Cruddur
17. go to the AWS console and verify that a second user was created. We will use handle of the second user 
18. create a conversation.py script and copy over conversation from Andrew's repository
19. create script for seeding data into cruddur-messages DynamoDB table, seed.py. Note: I chose to create it as .py script to run Python unit tests on it later.
```python
#!/usr/bin/env python3


import boto3
import os
import sys
from datetime import datetime, timedelta, timezone
import uuid

from conversation import *


current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, '..', '..'))
sys.path.append(parent_path)
from lib.db import db

# change this to your conversation; hardcoded for now
message_group_uuid = "5ae290ed-55d1-47a0-bc6d-fe2bc2700399"

def create_message_group(client,message_group_uuid, my_user_uuid, last_message_at=None, message=None, other_user_uuid=None, other_user_display_name=None, other_user_handle=None):
    table_name = 'cruddur-messages'
    record = {
        'pk':   {'S': f"GRP#{my_user_uuid}"},
        'sk':   {'S': last_message_at},
        'message_group_uuid': {'S': message_group_uuid},
        'message':  {'S': message},
        'user_uuid': {'S': other_user_uuid},
        'user_display_name': {'S': other_user_display_name},
        'user_handle': {'S': other_user_handle}
    }

    response = client.put_item(
        TableName=table_name,
        Item=record
    )
    print(response)

def create_message(client,message_group_uuid, created_at, message, my_user_uuid, my_user_display_name, my_user_handle):
  table_name = 'cruddur-messages'
  record = {
    'pk':   {'S': f"MSG#{message_group_uuid}"},
    'sk':   {'S': created_at },
    'message_uuid': { 'S': str(uuid.uuid4()) },
    'message': {'S': message},
    'user_uuid': {'S': my_user_uuid},
    'user_display_name': {'S': my_user_display_name},
    'user_handle': {'S': my_user_handle}
  }
  # insert the record into the table
  response = client.put_item(
    TableName=table_name,
    Item=record
  )
  # print the response
  print(response)

def get_user_uuids():
  sql = """
    SELECT 
      users.uuid,
      users.display_name,
      users.handle
    FROM users
    WHERE
      users.handle IN(
        %(my_handle)s,
        %(other_handle)s
        )
  """

  # change handles to my Cognito users
  users = db.query_array_json(sql,{
    'my_handle':  'olleyt', 
    'other_handle': 'bestie'
  })
  my_user    = next((item for item in users if item["handle"] == 'olleyt'), None)
  # get user from dictionary users by key "handle" and value 'bayko':
  
  other_user = next((item for item in users if item["handle"] == 'bestie'), None)
  results = {
    'my_user': my_user,
    'other_user': other_user
  }
  print('get_user_uuids')
  print(results)
  return results


# below shall be __init__ or __main__ 
def main():
    
    # this is also repeated in create_table script
    kwargs = {
    'endpoint_url': 'http://localhost:8000'
    }

    if len(sys.argv) == 2:
        if "prod" in sys.argv[1]:
            kwargs = {}
        
    ddb = boto3.client('dynamodb', **kwargs)

    # strip extra lines and make an array of lines from it
    lines = conversation.lstrip('\n').rstrip('\n').split('\n')
    users = get_user_uuids()
    now = datetime.now(timezone.utc).astimezone()


    # create message groups: one for current user and another for other user:
    create_message_group(
        client=ddb,
        message_group_uuid=message_group_uuid,
        my_user_uuid=users['my_user']['uuid'],
        other_user_uuid=users['other_user']['uuid'],
        other_user_handle=users['other_user']['handle'],
        other_user_display_name=users['other_user']['display_name'],
        last_message_at=now.isoformat(),
        message="this is a filler message"
        )

    create_message_group(
        client=ddb,
        message_group_uuid=message_group_uuid,
        my_user_uuid=users['other_user']['uuid'],
        other_user_uuid=users['my_user']['uuid'],
        other_user_handle=users['my_user']['handle'],
        other_user_display_name=users['my_user']['display_name'],
        last_message_at=now.isoformat(),
        message="this is a filler message"
        )

    
    for line_idx, line in enumerate(lines):
        if line.startswith('Person 1: '):
            key = 'my_user'
            message = line.replace('Person 1: ', '')
        elif line.startswith('Person 2: '):
            key = 'other_user'
            message = line.replace('Person 2: ', '')
        else:
            # change to logger
            print(line)
            raise 'invalid line'

        created_at = (now + timedelta(minutes=line_idx)).isoformat()
        create_message(
            client=ddb,
            message_group_uuid=message_group_uuid,
            created_at=created_at,
            message=message,
            my_user_uuid=users[key]['uuid'],
            my_user_display_name=users[key]['display_name'],
            my_user_handle=users[key]['handle']
        ) 

if __name__ == "__main__":
    main()

```
Note: Andrew changed his mind and we will not prepend sk with 'GRP#' for message groups

18. as we previously deleted our table, re-load the schema
19. temporarily change db.py to connect to prod RDS to get the users' data as we set them up for Cognito, go to line 18 and change CONNECTION_URL to PROD_CONNECTION_URL
20. test the seed script from /backend-flask/bin/ddb by running command ```python3 seed.py```. For production it'd be better to use batch write than executing bunch of puts

#### Scan 
21. create a script named 'scan' in the ddb folder:
```python
#!/usr/bin/env python3

import boto3

# we will not use scans for production
attrs = {
  'endpoint_url': 'http://localhost:8000'
}
ddb = boto3.resource('dynamodb',**attrs)
table_name = 'cruddur-messages'

table = ddb.Table(table_name)
response = table.scan()

items = response['Items']
for item in items:
  print(item)
```
22. make this script executable : ``` chmod u+x ./scan ```
23. run ```./scan``` and you shall see records from the loaded converstaion like one below:
```
{'user_uuid': 'd1f1f69e-e5e3-40d6-a43a-8d89bcca8c61', 'user_handle': 'bestie', 'sk': '2023-03-29T09:45:13.050615+00:00', 'pk': 'MSG#5ae290ed-55d1-47a0-bc6d-fe2bc2700399', 'message_uuid': 'a9fa7523-61db-46c1-b8f0-ea97e6c02de9', 'message': "Definitely. I think his character is a great example of the show's ability to balance humor and heart, and to create memorable and beloved characters that fans will cherish for years to come.", 'user_display_name': 'Alter Ego'}
```
#### Implement Pattern Scripts for Read and List Conversations
24. create folder patterns inside ddb folder
25. create files: get-conversation and list-conversations. Note that we need to specify 'TOTAL' on returned capacity to see how expensive our query is. We are getting messages belonging to a conversation by pk = MSG#message_group_uuid:
```python
#!/usr/bin/env python3

import boto3
import sys
import json
import datetime

attrs = {
  'endpoint_url': 'http://localhost:8000'
}

if len(sys.argv) == 2:
  if "prod" in sys.argv[1]:
    attrs = {}

dynamodb = boto3.client('dynamodb',**attrs)
table_name = 'cruddur-messages'

message_group_uuid = "5ae290ed-55d1-47a0-bc6d-fe2bc2700399"

year = str(datetime.datetime.now().year)
# define the query parameters
query_params = {
  'TableName': table_name,
  'ScanIndexForward': False,
  'Limit': 20,
  'ReturnConsumedCapacity': 'TOTAL',
  'KeyConditionExpression': 'pk = :pk AND begins_with(sk,:year)',
  #'KeyConditionExpression': 'pk = :pk AND sk BETWEEN :start_date AND :end_date',
  'ExpressionAttributeValues': {
    ':year': {'S': year },
    #":start_date": { "S": "2023-03-01T00:00:00.000000+00:00" },
    #":end_date": { "S": "2023-03-19T23:59:59.999999+00:00" },
    ':pk': {'S': f"MSG#{message_group_uuid}"}
  }
}


# query the table
response = dynamodb.query(**query_params)

# print the items returned by the query
print(json.dumps(response, sort_keys=True, indent=2))

# print the consumed capacity
print(json.dumps(response['ConsumedCapacity'], sort_keys=True, indent=2))

items = response['Items']
items.reverse()

for item in items:
  sender_handle = item['user_handle']['S']
  message       = item['message']['S']
  timestamp     = item['sk']['S']
  dt_object = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
  formatted_datetime = dt_object.strftime('%Y-%m-%d %I:%M %p')
  print(f'{sender_handle: <12}{formatted_datetime: <22}{message[:40]}...')
```
26. chmod u+x and run the script from the terminal. You shall see the conversation with json printed nicely.
27. Notice that we also implemented a filter on the sort key as Kirk suggested. Andrew put a comments for filtering messages between start and end dates but we will proceed with filtering by year for now.
28. implement ```list-conversations```
29. insert code
30. run ```chmod u+x ./list-conversations```
31. run ``` ./list_conversations```
32. expected response shall be similar to mine
```
gitpod /workspace/aws-bootcamp-cruddur-2023/backend-flask/bin/ddb/patterns (main) $ ./list-conversations 
 SQL STATEMENT--value-------

    SELECT 
      users.uuid
    FROM users
    WHERE
      users.handle =%(handle)s
   {'handle': 'olleyt'} 

my-uuid: 48c078df-8331-4715-a58d-0c0494496d02
{
  "ConsumedCapacity": {
    "CapacityUnits": 0.5,
    "TableName": "cruddur-messages"
  },
  "Count": 1,
  "Items": [
    {
      "message": {
        "S": "this is a filler message"
      },
      "message_group_uuid": {
        "S": "5ae290ed-55d1-47a0-bc6d-fe2bc2700399"
      },
      "pk": {
        "S": "GRP#48c078df-8331-4715-a58d-0c0494496d02"
      },
      "sk": {
        "S": "2023-03-31T01:07:29.447128+00:00"
      },
      "user_display_name": {
        "S": "Alter Ego"
      },
      "user_handle": {
        "S": "bestie"
      },
      "user_uuid": {
        "S": "d1f1f69e-e5e3-40d6-a43a-8d89bcca8c61"
      }
    }
  ],
  "ResponseMetadata": {
    "HTTPHeaders": {
      "content-length": "445",
      "content-type": "application/x-amz-json-1.0",
      "date": "Fri, 31 Mar 2023 22:27:54 GMT",
      "server": "Jetty(9.4.48.v20220622)",
      "x-amz-crc32": "2276557303",
      "x-amzn-requestid": "124de0fd-7e38-4ef9-b40b-152f110f7d66"
    },
    "HTTPStatusCode": 200,
    "RequestId": "124de0fd-7e38-4ef9-b40b-152f110f7d66",
    "RetryAttempts": 0
  },
  "ScannedCount": 1
}
```
33. this completes implementation of DynamoDb utility scripts

## Create New Conversation

34. as I stopped RDS and shut down GitPod for the night, these actions need to be executed to proceed with the implementation:
    * start RDS in AWS console
    * run ```docker-compose up``` in GitPod
    * check connection to RDS with ```./backend-flask/bin/db/db-connect prod```
    * open Cruddur web application, sign out and sign in to refresh the token
36. go to backend-flask folder 
37. create a new Python script named 'ddb.py' with the code from Andrew's repository for week 5. 
38. Note 1: Ddb is a stateless class; Andrew said it is so much easier to test a stateless class than test with tracing of instance of a class, even though this approach results in a more verbose code 
39. Note 2: that for RDS we wrote generic functions and SQL queries but for DynamoDB we will use more explicit queries for the application dictated by access patterns 
40. Note 3: we could have used environment variables (or feature flags) for table name to denote environment stage such as 'dev', 'test', 'prod' and use them as table prefix for example
41. add 'ScanIndexforward' for explicit order in ddb/list-conversation script (line 44)
42. go back to backend-flask folder and amend app.py:
    * find route ```/api/message-groups```, note that handle was hardcoded and we will change this code now to the cognito user id; it is called 'sub' in the AWS Cognito User Pool
43. Then create a folder ./backend-flask/bin/cognito and create a script called ```list-users``` with the code from Andrew's repository
44. run ```chmod u+x ./list-users```
45. add list cognito user in the IAM policy for Cruddur (since we follow the principle of least priviledge)
46. temporarily set environment variable ```AWS_COGNITO_USER_POOL``` and also add it to the docker compose file
47. add package.json and and package-json.lock into .gitattributes
48. create file ./backend-flask/bin/db/update_cognito_user_ids, copy the code from Andrew's repository then run chmod u+x on it
49. add for the setup script: ```source $bin_path/db/update_cognito_user_ids```
50. ```Note 4:``` db-setup script for RDS needs modification for my Cognito users since I don't use mocked users anymore. seed.sql also need to be updated with my own users 
51. added 'params' in method signature for 'query_commit' in db.py. Remember I run it with python3 command instead of source
52. go back to app.py and change code for route ```/api/message_groups```: get message gropu with cognito user id (see the commit history for week 5)
53. change code for ```./services/message_groups.py``` (see the commit history for week 5)
54. when we tried to login to Cruddur and see messages, we got 401 error and back-end logs showed an error 'token is not passed along'
55. Bearer token needs to be passed along to these pages:
    * HomeFeed.js
    * MessageGroups.js
    * MessageGroup.js
    * MessageForm.js
56. amend code for ```HomeFeedPage.js``` (see the commit history for week 5)
57. correct code for method query_value, line 91 in db.py (see the commit history for week 5). Andrew was getting an error because his users were not updated with cognito user ids
58. abstract checking authentication with Cognito in a separate JavaScript function ```CheckAuth.js```
59. in ./frontend-react-js/src folder create new folder *lib*
60. ```Note 5:``` "This is a filler message" comes from seed.py script for DynamoDB (ddb) when we created a mocked conversation. 
61. implement changes for ```MessageGroupPage.js``` (see commit history)
62. re-create DynamoDB table and the conversation: 
    ```bash
        ./bin/ddb/schema-load
        ./bin/ddb/seed
        ./bin/ddb/patterns/list-conversations
    ```
63. implement changes for MessageGroupItem.js (see commit history)
64. Now we need to implement changes for back-end. Go back to app.py as we need to add authentication to stop people reading other people's conversations
65. implement changes for messages.py script
66. implement changes for method list-messages in ddb.py
67. go back to frontend-react-js
68. implement changes for MessageForm.js for creating messages
69. update ./backednd-flask/app.py for route ```api/messages``` with methods 'POST', 'OPTIONS'
70. implement changes for ```create_messages.py``` (copy code from Andrew's repository). We added 'mode' parameter to create messageto differentiate if we want to update a conversation or to create a new message group
71. implement changes for ./lib/ddb.py : add create_message function. Note that this function generates uuid for us. Andrew noted: "we should propbably check that put operation for the DynamoDb table was successful before returning results"
72. ```Note 6:``` 'credential provider' error that Andrew was facing was misleading and he had to compose down and up Cruddur containers
73. create a new SQL script: ```./backend-flask/db/sql/users/create_message_users.sql``` where we shall be able to separate sender and receiver     

## Create New Message
74. implement changes in App.js (see commit history)
75. create new page MessageGroupNewPage.js with the code from Andrew's repository (see commit history)
76. sign up a new user called Londo Mollari with handle @londo as a test user for new converstaion. Andrew added his 3rd user to seed data script. I added a new user by signing it up in Cruddur on a separate email account so it was stored in RDS and registered in Cognito User pool
77. next we needed to add a new service and a script user_short.sql to be able to send this new user a message. Note that we don't need to protect this endpoint because we are dealing with publicly available information here
78. update MessageGroupFeed.js for getting other user's handle and adding a new message item. We also needed to take care about user redirection on a new conversation page if a new conversation started
79. update create_message.py to cater for creating a new conversation case in lines 71-80 when we added ```elif(mode == 'create')```
80. update ddb.py method to create message group. We need to create conversation from current user perspective and another conversation from other user perspective and then return message data structure. Check that we pass message (around line 74)
81. side tracked with post-confirmation Lamba error 'function takes 2 arguments, 5 given). That was because I used unpacking for params tuple in line 26. It shall be just params without unpacking. I need to investigate later why it is the case now and what we have changed in db.py to chang this Lambda function behaviour
82. Now we shall be able to loging to Cruddur, go to Messages and append /new/londo and send a message to start a new conversation with Londo
   
we created a new user Londo Mollari with handle 'londomollari'.
So that when we append messages/new/londomollari, a filler conversation appear:
![filler_conversation](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/b34e0322ee61f68a27fa27c0ddb077eefe9ce23a/_docs/assets/filler_conversation.png)

If we post a message in this filler conversation, we are redirected to the new conversation and see the posted message:
![comversation_londo](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/b34e0322ee61f68a27fa27c0ddb077eefe9ce23a/_docs/assets/new_conversation_londo.png)

## Implementing DynamoDB Streams
83. it's time to implement DynamoDB base table and GSI in AWS. We will do it with ddb/schema-load script + AWS console (for now)
84. I added a policy for my AWS user for DynamoDB since I am adhering to the principle of the least priviledge and do not use an Admin user
85. go to Gitpod, folder ./backend-flask/bin/ddb
86. run ```./schema-load prod```
87. check AWS DynamoDB console that table 'cruddur-messages' was created
88. go to tab 'Exports and Streams'
89. scroll down to 'DynamoDB Stream Details'
90. click on 'Turn On' button
91. choose 'New Image'
92. click on 'Turn on stream' button at the bottom of the form. This will create a DynamoDB stream
93. Next we need to add VPC Endpoint Gateway for the DynamoDB table
94. go to VPC in AWS console
95. choose 'Endpoints' on the left hand side
96. create an endpoint, name tag = ddb_cruddur, service category = AWS Services. 
97. in services, search for DynamoDB and tick the box next to it when found
98. choose the default VPC and associated route table
99. leave 'Policy' with default value 'Full access'
100. click 'Create Endpoint'
101. Andrew noted that transactions are hard to implement in DynamoDB and we are not doing that (at this point)
102. Next we need to implement Lambda function that will insert a message into conversation via DynamoDB stream
    * function name: cruddur_messaging_stream
    * Andrew chose to use `create new basic role` but we will add more permissions for Lambda to access DynamoDB later
    * go to IAM and create policy [cruddur-message-stream-policy.json](https://github.com/olleyt/aws-bootcamp-cruddur-2023/blob/276a8e18929f0988e60c34d1234d1b4353a93dae/aws/policies/cruddur-message-stream-policy.json)
    * attach this policy to our lambda role
    * in advanced settings, tick 'enable VPC'
    * choose same subnets that were chosen for the RDS (us-east-1a, us-east-1b)
    * choose default security group that was chosen for the RDS instance
    * create function
    * copy Andrew's code from week5-again-again branch
    * click on 'Deploy' button
    * go to 'Configuration', then 'Permissions' tab
    * click on the role link
    * in the opened up tab add policy 'AWSLambdainvocation-DynamoDb' policy to this role. Note that we left resources as all ('*') 

### Adding GSI to DynamoDB
103. first we need to delete the existing DynamoDB table 'cruddur-messages' as we will re-create it with the GSI via ddb/schema-load script
104. copy the GSI code from Andrew's repository and add it to the ddb/schema-load script
105. run ```./ddb/schema-load prod``` to recreate DynamoDB table 'cruddur-messages' in AWS
106. add streams as in steps 89-92 above
107. add trigger below: choose Lambda function cruddur_messaging_stream and set batch size = 1
108. go to GitPod, open docker-compose.yml file and comment out AWS_ENDPOINT_URL variable. This will force our back-end container to connect to AWS DynamoDB table, not the local one
109. Go to the Cruddur web app, sign out, sign in, go to 'Messages'
110. append the url with /new/londo 
111. now we shall be able to send new mesage to londo and see no errors in CloudWatch logs


## Troubleshooting

* if a new GitPod instance was started and/or if there is an error in backend-flask container logs: 'CIDR block /32 is malformed':
    * GitPod IP address was changed
    * run these commands as command in docker.yml is not picked up: 
        ```bash
         export GITPOD_IP=$(curl ifconfig.me)
         source  "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds/rds-update-sg-rule"
        ``` 
* Check that RDS is up & running
* Check that connection url is using current password from Secret Manager
* Check that post-confirmation Lambda environment variable is using current password from Secret Manager. The password is rotated regularly.
* Check that db.py is pointed to production RDS as we source user data from AWS Cognito pool
* run ```docker-compose up``` to make local DynamoDB instance and Cruddur application available
* Since I turned off pre-builds, new GitPod instances did not update GitPod IP automatically so I needed to run these commands as pre-requisite before testing utility:
```bash
export GITPOD_IP=$(curl ifconfig.me)
source  "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds/rds-update-sg-rule"
```  
* if a new GitPod isntance was spinned up, local DynamoDB table need to be re-created and re-seeded from ./backend-flask/bin/ddb:
```
./schema-load
./list-tables
./python3 seed.py
```

### GitPod environment variables did not propagate
* issue: env variables did not propagate to docker containters 
* back-end container was using old database password
* I had to set CONNECTION_URL as PROD_CONNECTION_URL to use production RDS while Docker backedn container was using CONNECTION_URL. This was conflicting with local database setup. ```./bin/ddb/patterns/list-conversations``` needed PROD_CONNECTION_URL to get user ids from Cognito and production RDS in AWS, but the backend-flask Docker container used CONNECTION_URL for connection to PostgreSQL database

## Resources
- [Python args vs kwargs](https://realpython.com/python-kwargs-and-args/)
- [Python enumerate](https://realpython.com/python-enumerate/)
- [Import Python modules](https://realpython.com/python-modules-packages/)
- DynamoDB / Client / [create_table](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/create_table.html)
- [Python Script Not Showing Output](https://www.shellhacks.com/python-script-not-showing-output-solved/)
- [DynamoDB examples using SDK for Python (Boto3)](https://docs.aws.amazon.com/code-library/latest/ug/python_3_dynamodb_code_examples.html)
- [Git Concepts I Wish I Knew Years Ago](https://dev.to/g_abud/advanced-git-reference-1o9j#commit-messages)
- [Customizing Git Attributes](https://git-scm.com/book/en/v2/Customizing-Git-Git-Attributes#:~:text=gitattributes%20file%20in%20one%20of,file%20committed%20with%20your%20project.)
- [Please Add .gitattributes To Your Git Repository](https://dev.to/deadlybyte/please-add-gitattributes-to-your-git-repository-1jld)
