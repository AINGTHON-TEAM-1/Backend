# Rule: RLS Performance

## Problem
Complex Row-Level Security (RLS) policies can slow down every query as they are evaluated for every row.

## Solution
1. Use `STABLE` or `IMMUTABLE` functions for policy checks.
2. Ensure columns used in RLS policies are indexed.
3. Avoid subqueries in policies; use `auth.uid()` or simple joins.

### Bad Pattern
```sql
CREATE POLICY "Users can see their own reports" ON reports
FOR SELECT USING (
  user_id IN (SELECT id FROM profiles WHERE id = auth.uid())
);
```

### Good Pattern
```sql
CREATE POLICY "Users can see their own reports" ON reports
FOR SELECT USING (
  user_id = auth.uid()
);
```
