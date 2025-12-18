# Database Management

## Viewing Database Contents

### Option 1: Using the Python Script (Recommended)

**Inside Docker:**

```powershell
docker compose exec pharmacy-agent python /app/backend/view_db.py
```

**Locally:**

If your local database has schema issues, first reset it:

```powershell
cd backend
python reset_local_db.py
```

Then view it:

```powershell
python view_db.py
```

## Deleting Database Records

### Option 1: Using the Python Script (Interactive Menu)

**Inside Docker:**

```powershell
docker compose exec pharmacy-agent python /app/backend/delete_db_records.py
```

**Locally:**

```powershell
cd backend
python delete_db_records.py
```

This interactive menu allows you to:
- Delete all tickets/reservations
- Delete a specific ticket by ID
- Delete all tickets for a specific user
- Delete a specific user (and their tickets/prescriptions)
- Delete all prescriptions
- List users and tickets

### Option 2: Direct SQL Commands

**Inside Docker:**
```powershell
docker compose exec pharmacy-agent sqlite3 /data/app.db
```

**Locally:**
```powershell
cd backend
sqlite3 app.db
```

Then run SQL commands:
```sql
-- Delete all tickets
DELETE FROM tickets;

-- Delete a specific ticket by ID
DELETE FROM tickets WHERE id = 'ticket-id-here';

-- Delete tickets for a specific user
DELETE FROM tickets WHERE user_id = 'user-id-here';

-- Delete all tickets without a user_id (old reservations)
DELETE FROM tickets WHERE user_id IS NULL;

-- Delete a specific user (delete related records first!)
DELETE FROM tickets WHERE user_id = 'user-id-here';
DELETE FROM prescriptions WHERE user_id = 'user-id-here';
DELETE FROM users WHERE id = 'user-id-here';

-- View all tickets
SELECT * FROM tickets;

.quit  -- Exit
```

## Resetting the Local Database

If your local `backend/app.db` has schema issues (missing columns), reset it:

```powershell
cd backend
python reset_local_db.py
```

This will:
1. Delete the old database
2. Create a new one with the correct schema
3. Seed it with initial data

## Option 2: Using SQLite directly

If you want to use SQLite command-line tools:

### Inside Docker:
```powershell
docker compose exec pharmacy-agent sqlite3 /data/app.db
```

Then run SQL queries:
```sql
.tables                    -- List all tables
SELECT * FROM users;       -- View all users
SELECT * FROM medications; -- View all medications
SELECT * FROM inventory;   -- View inventory
SELECT * FROM prescriptions; -- View prescriptions
SELECT * FROM tickets;     -- View tickets/reservations
.quit                      -- Exit
```

### Locally (if database is in backend/):
```powershell
cd backend
sqlite3 app.db
```

## Option 3: Using a SQLite GUI Tool

You can use tools like:
- **DB Browser for SQLite** (https://sqlitebrowser.org/)
- **DBeaver** (https://dbeaver.io/)
- **VS Code SQLite extension**

Connect to:
- **Docker**: Copy the database file from the container first, or mount it as a volume
- **Local**: `backend/app.db` (if running locally)

To copy from Docker:
```powershell
docker compose cp pharmacy-agent:/data/app.db ./app.db
```

