CREATE TABLE User (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE Solde (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    value INTEGER NOT NULL
);

CREATE TABLE Frais (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    content TEXT,
    FOREIGN KEY(user_id) REFERENCES User(id)
);