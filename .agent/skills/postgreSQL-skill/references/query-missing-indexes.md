# Rule: Missing Indexes

## Problem
Queries scanning entire tables (Sequential Scan) instead of using indexes (Index Scan) lead to high CPU usage and slow response times.

## Solution
Create indexes on columns used in `WHERE`, `JOIN`, `ORDER BY`, and `GROUP BY` clauses.

### Bad Pattern
```sql
-- Query without index on user_id
SELECT * FROM reports WHERE user_id = '123';
```

### Good Pattern
```sql
CREATE INDEX idx_reports_user_id ON reports(user_id);
```

## How to Verify
Use `EXPLAIN ANALYZE` to check for "Index Scan".
