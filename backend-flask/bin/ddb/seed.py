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
