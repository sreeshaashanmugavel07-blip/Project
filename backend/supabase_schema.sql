-- Create complaints table in Supabase
-- Run this SQL in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS complaints (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    issue_type TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    phone TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create an index on timestamp for faster queries
CREATE INDEX IF NOT EXISTS idx_complaints_timestamp ON complaints(timestamp DESC);

-- Create an index on issue_type for filtering
CREATE INDEX IF NOT EXISTS idx_complaints_issue_type ON complaints(issue_type);

-- Enable Row Level Security (RLS) - Optional: Adjust based on your needs
ALTER TABLE complaints ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations (adjust based on your security needs)
-- For production, you might want to add authentication-based policies
CREATE POLICY "Allow all operations" ON complaints
    FOR ALL
    USING (true)
    WITH CHECK (true);
