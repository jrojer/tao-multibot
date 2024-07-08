-- Postgres SQL

ALTER TABLE chat_messages
ADD COLUMN function_name TEXT;

ALTER TABLE chat_messages
ADD COLUMN function_args TEXT;
