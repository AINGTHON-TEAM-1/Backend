# Rule: Connection Pooling

## Problem
In serverless or high-concurrency environments, creating a new database connection for every request is expensive and can exceed `max_connections`.

## Solution
Use a connection pooler like **Supavisor** (integrated in Supabase). Connect using the pooling port (usually 6543) instead of the direct port (5432).

## Key Settings
- **Transaction Mode**: Recommended for serverless/lambdas.
- **Session Mode**: Required for features like `LISTEN/NOTIFY`.
