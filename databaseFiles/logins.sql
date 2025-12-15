-- database: /workspaces/2026SE_Task1_MAXH/databaseFiles/database.db

CREATE TABLE IF NOT EXISTS devlog (
    email TEXT UNIQUE NOT NULL,
    developer text NOT NULL,
    project text NOT NULL,
    devlog TEXT,
    startdate TIMESTAMP NOT NULL,
    endate TIMESTAMP NOT NULL,
    timeworked INT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    repo text 
);