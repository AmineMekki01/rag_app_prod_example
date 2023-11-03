-- migrate:up

CREATE TABLE message (
    id SERIAL PRIMARY KEY,
    model VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    answer TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- migrate:down
DROP TABLE IF EXISTS message;