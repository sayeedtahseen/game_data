CREATE TABLE IF NOT EXISTS teams (
    id            INTEGER PRIMARY KEY,
    conference    VARCHAR(10),
    division      VARCHAR(20),
    city          VARCHAR(50),
    name          VARCHAR(50),
    full_name     VARCHAR(100),
    abbreviation  VARCHAR(5)
);
