-- Run this once to set up a basic table structure
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount DECIMAL(10, 2),
    is_suspicious BOOLEAN
);

INSERT INTO transactions (user_id, amount, is_suspicious) VALUES (101, 5000.00, 1);