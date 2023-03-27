from datetime import datetime, timedelta, timezone
from opentelemetry import trace

#from lib.db import pool, query_wrap_array
from  lib.db import db

tracer = trace.get_tracer("home.activities")

class HomeActivities:
  def run(logger, cognito_user_id=None):
    logger.info('Hello Cloudwatch! from  /api/activities/home')
    with tracer.start_as_current_span("home-activities-mock-data"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())

      sql = db.template('activities','home')
      results = db.query_array_json(sql)
       # span.set_attribute("app.result-length", len(results))
      return results
    
    """
       with pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(sql)
          # this will return a tuple
          # the first field being the data
          json = cur.fetchone()
      return json[0] 
    """