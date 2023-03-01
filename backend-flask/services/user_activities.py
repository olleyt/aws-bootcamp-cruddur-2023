import os
from datetime import datetime, timedelta, timezone
# import XRay SDK libraries
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

# Initialize the X-Ray recorder
xray_url = os.getenv("AWS_XRAY_URL")
xray_recorder.configure(service='user-activities-service', dynamic_naming=xray_url)
#xray_recorder.configure(service='user-activities-service')
patch_all()
#XRayMiddleware(app, xray_recorder)


class UserActivities:
  def run(user_handle):
    try:
      # Start a segment
      segment = xray_recorder.begin_segment('user_activities_segment')
      
      model = {
        'errors': None,
        'data': None
      }

      now = datetime.now(timezone.utc).astimezone()
      # Add metadata or annotation here if necessary
      xray_dict = {'now': now.isoformat()}
      segment.put_metadata('now', xray_dict, 'namespace')

      if user_handle == None or len(user_handle) < 1:
        model['errors'] = ['blank_user_handle']
      else:
        # Start a subsegment
        subsegment = xray_recorder.begin_subsegment('user_activities_subsegment')
        now = datetime.now()
        results = [{
          'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
          'handle':  'Andrew Brown',
          'message': 'Cloud is fun!',
          'created_at': (now - timedelta(days=1)).isoformat(),
          'expires_at': (now + timedelta(days=31)).isoformat()
        }]
        model['data'] = results
        xray_dict['results'] = len(model['data'])
        subsegment.put_metadata('results', xray_dict, 'user_activities_results_ns')
    finally:  
      # Close the segment
      xray_recorder.end_subsegment()
    return model