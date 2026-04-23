CREATE TABLE IF NOT EXISTS games (
    game_id             INTEGER PRIMARY KEY,
    date                TIMESTAMPTZ,
    season              INTEGER,
    status              VARCHAR(50),
    period              INTEGER,
    time                VARCHAR(20),
    postseason          BOOLEAN,
    home_team_score     INTEGER,
    visitor_team_score  INTEGER,
    home_team_id        INTEGER REFERENCES teams(id),
    home_team_name      VARCHAR(50),
    home_team_abb       VARCHAR(5),
    visitor_team_id     INTEGER REFERENCES teams(id),
    visitor_team_name   VARCHAR(50),
    visitor_team_abb    VARCHAR(5)
);
