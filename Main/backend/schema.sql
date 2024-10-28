DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS portfolio;
DROP TABLE IF EXISTS eventLog;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(100) NOT NULL,
  totalCash DECIMAL(15,2)
);

CREATE TABLE portfolio (
    ticker VARCHAR(10) UNIQUE NOT NULL,
    numShares INTEGER,
    id INTEGER,
    FOREIGN KEY (id) REFERENCES user(id)
);

CREATE TABLE eventLog (
    id INTEGER,
    eventName TEXT CHECK(eventName IN ('Bought', 'Sold', 'Logged on', 'Logged out')) NOT NULL,
    stockSold VARCHAR(10),
    stockBought VARCHAR(10),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id) REFERENCES user(id)
);

