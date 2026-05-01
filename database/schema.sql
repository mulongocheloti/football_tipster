CREATE TABLE teams(
team_id INT PRIMARY KEY,
team_name TEXT
);

CREATE TABLE matches(
match_id BIGINT PRIMARY KEY,
competition_code TEXT,
season INT,
utc_date TIMESTAMP,
matchday INT,
home_team_id INT,
away_team_id INT,
home_goals INT,
away_goals INT,
status TEXT
);

CREATE TABLE standings(
competition_code TEXT,
team_id INT,
season INT,
position INT,
played INT,
wins INT,
draws INT,
losses INT,
points INT,
PRIMARY KEY (season, competition_code, team_id)
);

CREATE TABLE team_blacklist(
team_id INT PRIMARY KEY,
team_name TEXT
);

INSERT INTO team_blacklist (team_id, team_name) VALUES
(108, 'Inter'),
(4, 'Dortmund'),
(109, 'Juventus'),
(64, 'Liverpool'),
(100, 'Roma'),
(548, 'Monaco'),
(73, 'Tottenham'),
(512, 'Brest'),
(110, 'Lazio'),
(322, 'Hull'),
(69, 'QPR'),
(102, 'Atalanta'),
(516, 'Marseille'),
(721, 'Leipzig');

CREATE TABLE tips (
    match_id INT PRIMARY KEY,
    utc_date TIMESTAMP,
    home_position INT,
    away_position INT,
    points_difference INT,
    prediction VARCHAR(10),
    confidence INT,
    flag TEXT,
    home_form VARCHAR(10),
    away_form VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- This table records what data was last synced for each competition.
CREATE TABLE api_sync_log(
competition_code VARCHAR(10),
season INT,
last_standings_sync TIMESTAMP,
PRIMARY KEY(competition_code,season)
);


CREATE TABLE IF NOT EXISTS tip_results (
    match_id        BIGINT PRIMARY KEY,
    utc_date        TIMESTAMP,
    competition_code TEXT,
    home_team       TEXT,
    away_team       TEXT,
    home_goals      INT,
    away_goals      INT,
    actual_result   VARCHAR(10),   -- HOME_WIN | DRAW | AWAY_WIN
    prediction      VARCHAR(10),   -- copied from tips
    confidence      INT,           -- copied from tips
    flag            TEXT,          -- copied from tips
    home_form       VARCHAR(10),   -- copied from tips
    away_form       VARCHAR(10),   -- copied from tips
    outcome         VARCHAR(10),   -- WIN | LOSS
    validated_at    TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- ROW LEVEL SECURITY (RLS)
-- ==========================================

-- Enable RLS on all tables
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE standings ENABLE ROW LEVEL SECURITY;
ALTER TABLE tips ENABLE ROW LEVEL SECURITY;
ALTER TABLE tip_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_blacklist ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_sync_log ENABLE ROW LEVEL SECURITY;

-- Public read access for frontend-facing tables
CREATE POLICY "Public read" ON tips FOR SELECT USING (true);
CREATE POLICY "Public read" ON matches FOR SELECT USING (true);
CREATE POLICY "Public read" ON standings FOR SELECT USING (true);
CREATE POLICY "Public read" ON teams FOR SELECT USING (true);
CREATE POLICY "Public read" ON tip_results FOR SELECT USING (true);

-- team_blacklist and api_sync_log: no policy = anon access fully blocked