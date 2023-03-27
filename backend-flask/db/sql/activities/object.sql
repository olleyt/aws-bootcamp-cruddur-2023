SELECT 
  activities.uuid,
  users.display_name,
  users.handle,
  activities.message,
  activities.created_at,
  activities.expires_at
FROM public.activities activities
INNER JOIN public.users on users.uuid = activities.user_uuid
WHERE
  activities.uuid = %(uuid)s