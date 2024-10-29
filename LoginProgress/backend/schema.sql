DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS portfolio;
DROP TABLE IF EXISTS eventLog;



CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    totalCash REAL DEFAULT 10000.0
);


CREATE TABLE portfolio (
    ticker VARCHAR(10) UNIQUE NOT NULL,
    id INTEGER,
    FOREIGN KEY (id) REFERENCES user(id)
);

CREATE TABLE eventLog (
    id INTEGER,
    event TEXT NOT NULL CHECK(event IN ('Bought', 'Sold', 'Logged on', 'Logged out')),
    stockSold VARCHAR(10),
    stockBought VARCHAR(10),
    timeLoggedOn DATETIME,
    timeLoggedOff DATETIME,
    FOREIGN KEY (id) REFERENCES user(id)
);
