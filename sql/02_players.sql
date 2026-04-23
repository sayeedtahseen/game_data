CREATE TABLE IF NOT EXISTS players (
    id          INTEGER PRIMARY KEY,
    first_name  VARCHAR(100),
    last_name   VARCHAR(100),
    team_id     INTEGER REFERENCES teams(id)
);
