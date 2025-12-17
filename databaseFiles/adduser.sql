-- database: /workspaces/2026SE_Task1_MAXH/databaseFiles/database.db

CREATE TABLE IF NOT EXISTS twoFa (
    email TEXT UNIQUE NOT NULL,
    otp text NOT NULL,
    expiry TIMESTAMP NOT NULL
);
