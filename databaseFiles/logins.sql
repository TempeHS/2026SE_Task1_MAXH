-- database: /workspaces/2026SE_Task1_MAXH/databaseFiles/database.db

CREATE TABLE IF NOT EXISTS logins (
    UID INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);