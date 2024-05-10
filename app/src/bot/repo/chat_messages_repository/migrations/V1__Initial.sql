-- Postgres SQL

CREATE TABLE chat_messages (
    id TEXT PRIMARY KEY,
    timestamp INT NOT NULL,
    content TEXT NOT NULL,
    content_type TEXT NOT NULL,
    username TEXT NOT NULL, 
    chat TEXT NOT NULL,
    messenger TEXT NOT NULL,
    role TEXT NOT NULL,
    bot TEXT NOT NULL
);
