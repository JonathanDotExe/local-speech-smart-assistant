PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS rooms (
    id integer PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL
);

CREATE TABLE IF NOT EXISTS clients (
    id integer PRIMARY KEY AUTOINCREMENT,
    room_id integer,
    pkey text NOT NULL UNIQUE,
    client_name text NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms (id)
    ON UPDATE SET NULL
    ON DELETE SET NULL
);