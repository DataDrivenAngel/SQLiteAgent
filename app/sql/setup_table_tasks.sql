DROP TABLE IF EXISTS tasks;

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    context TEXT,
    goal TEXT NOT NULL,
    results TEXT,
    response TEXT,
    is_active boolean NOT NULL,
    iteration_limit INT,
    iterations INT
    );
