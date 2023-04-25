-- this file was manually created
INSERT INTO public.users (display_name, email, handle, cognito_user_id)
VALUES
  ('Olley T', 'g@gmail.com', 'olleyt' ,'MOCK'),
  ('Alter Ego', 'o..rt@gmail.com', 'bestie' ,'MOCK'),
  ('Londo Mollari','ol..va@gmail.com' ,'londomollari' ,'MOCK');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'olleyt' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )