import uuid
from datetime import datetime, timedelta, timezone
from lib.db import db


class CreateActivity:
    """
    class docstring
    """

    def run(message, user_handle, ttl):
        """
        run function
        """
        model = {
            'errors': None,
            'data': None
        }

        now = datetime.now(timezone.utc).astimezone()

        if (ttl == '30-days'):
            ttl_offset = timedelta(days=30)
        elif (ttl == '7-days'):
            ttl_offset = timedelta(days=7)
        elif (ttl == '3-days'):
            ttl_offset = timedelta(days=3)
        elif (ttl == '1-day'):
            ttl_offset = timedelta(days=1)
        elif (ttl == '12-hours'):
            ttl_offset = timedelta(hours=12)
        elif (ttl == '3-hours'):
            ttl_offset = timedelta(hours=3)
        elif (ttl == '1-hour'):
            ttl_offset = timedelta(hours=1)
        else:
            model['errors'] = ['ttl_blank']

        if user_handle == None or len(user_handle) < 1:
            model['errors'] = ['user_handle_blank']

        if message is None or len(message) < 1:
            model['errors'] = ['message_blank']
        elif len(message) > 280:
            model['errors'] = ['message_exceed_max_chars']

        if model['errors']:
            model['data'] = {
                'handle':  user_handle,
                'message': message
            }
        else:
            expires_at = (now + ttl_offset).isoformat()
            user_uuid = CreateActivity.create_activity(user_handle, message, expires_at)

            object_json = CreateActivity.query_object_activity(user_uuid)
            model['data'] = object_json
        return model

    def create_activity(handle, message, expires_at):
        """
        this method creates a crud and commits in RDS
        """
        sql = db.load_template('activities', 'create')
        params = {'handle': handle, 'message': message,
                  'expires_at': expires_at}
        user_uuid = db.query_commit(sql, params)
        return user_uuid

    def query_object_activity(user_uuid):
        """
        select crud data to show on front-end
        """
        sql = db.load_template('activities', 'object')
        params = {'uuid': user_uuid}
        return db.query_object_json(sql, params)
