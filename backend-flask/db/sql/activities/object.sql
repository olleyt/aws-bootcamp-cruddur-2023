SELECT 
  activities.uuid,
  users.display_name,
  users.handle,
  activities.message,
  activities.created_at,
  activities.expires_at
FROM public.activities
INNER JOIN public.users on users.uuid = activities.user_uuid
WHERE
  users.uuid = %(uuid)s
ORDER BY activities.created_at DESC 
LIMIT 1  