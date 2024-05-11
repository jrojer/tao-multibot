-- Postgres SQL

CREATE TABLE chat_messages (
    "id" TEXT PRIMARY KEY,
    "timestamp" INT NOT NULL,
    "content" TEXT NOT NULL,
    "content_type" TEXT NOT NULL,
    "user" TEXT NOT NULL, 
    "chat" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "role" TEXT NOT NULL,
    "added_by" TEXT NOT NULL
);
