DROP TABLE IF EXISTS tools;

CREATE TABLE IF NOT EXISTS tools (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    use TEXT NOT NULL,
    tool_body TEXT
    );
