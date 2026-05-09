# Rule: Data Integrity and Constraints

## Problem
Relying solely on application logic for data integrity can lead to inconsistent data when bugs occur or direct DB access is used.

## Solution
Use PostgreSQL constraints:
- `NOT NULL` for required fields.
- `UNIQUE` for business keys.
- `FOREIGN KEY` for relationships.
- `CHECK` for domain rules.

### Example
```sql
ALTER TABLE reports 
ADD CONSTRAINT check_price_positive CHECK (price >= 0);
```
