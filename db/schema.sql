DROP TABLE IF EXISTS user;

CREATE TABLE user (
    ip_address TEXT NOT NULL,
    filename TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);